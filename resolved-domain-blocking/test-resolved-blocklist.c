/* SPDX-License-Identifier: LGPL-2.1+ */

#include <net/if.h>
#include <linux/if.h>
#include <linux/rtnetlink.h>
#include <sys/socket.h>
#include <unistd.h>

#include "alloc-util.h"
#include "conf-parser.h"
#include "dns-domain.h"
#include "fd-util.h"
#include "fileio.h"
#include "log.h"
#include "resolved-conf.h"
#include "resolved-dns-blocklist.h"
#include "resolved-dns-query.h"
#include "resolved-dns-stub.h"
#include "resolved-etc-hosts.h"
#include "string-util.h"
#include "strv.h"

DEFINE_TRIVIAL_CLEANUP_FUNC(DnsTransaction*, dns_transaction_free);

static DnsQuestion *make_question(const char *name, uint16_t type) {
        _cleanup_(dns_resource_key_unrefp) DnsResourceKey *key = NULL;
        DnsQuestion *question;

        assert_se(key = dns_resource_key_new(DNS_CLASS_IN, type, name));
        assert_se(question = dns_question_new(1));
        assert_se(dns_question_add(question, key) >= 0);
        return question;
}

static void test_config(Manager *m, const char *path) {
        _cleanup_fclose_ FILE *f = NULL;

        assert_se(f = tmpfile());
        assert_se(fprintf(f, "[Resolve]\nBlockedDomainFile=/discarded\nBlockedDomainFile=\n"
                         "BlockedDomainFile=%s\nBlockedDomainFile=relative/path\nBlockedDomainFile=%s\n"
                         "BlockedDomainFile=/second/list\n", path, path) > 0);
        rewind(f);
        assert_se(config_parse(NULL, "test-resolved.conf", f, "Resolve\0", config_item_perf_lookup,
                               resolved_gperf_lookup, CONFIG_PARSE_WARN, m) >= 0);
        assert_se(strv_length(m->blocked_domain_files) == 2);
        assert_se(streq(m->blocked_domain_files[0], path));
        assert_se(streq(m->blocked_domain_files[1], "/second/list"));
        m->blocked_domain_files = strv_free(m->blocked_domain_files);
        assert_se(strv_extend(&m->blocked_domain_files, path) >= 0);
}

static void test_query_policy(Manager *m) {
        static const uint16_t types[] = {
                DNS_TYPE_A, DNS_TYPE_AAAA, DNS_TYPE_TXT, DNS_TYPE_MX, DNS_TYPE_PTR, DNS_TYPE_SRV,
                DNS_TYPE_CNAME, DNS_TYPE_DNSKEY, DNS_TYPE_ANY,
                64, 65, /* SVCB and HTTPS have no symbolic constants in v238. */
        };
        unsigned i;

        for (i = 0; i < ELEMENTSOF(types); i++) {
                _cleanup_(dns_question_unrefp) DnsQuestion *question = make_question("a.b.facebook.com", types[i]);
                _cleanup_(dns_query_freep) DnsQuery *q = NULL;
                unsigned transactions = m->n_transactions_total;

                assert_se(dns_query_new(m, &q, question, question, 0, SD_RESOLVED_DNS) >= 0);
                assert_se(dns_query_go(q) == 1);
                assert_se(q->state == DNS_TRANSACTION_RCODE_FAILURE);
                assert_se(q->answer_rcode == DNS_RCODE_NXDOMAIN);
                assert_se(!q->answer_authenticated);
                assert_se(!q->answer);
                assert_se(!q->candidates);
                assert_se(!q->timeout_event_source);
                assert_se(m->n_transactions_total == transactions);
        }

        /* Existing local synthesis retains its usual behaviour for an unblocked name. */
        {
                _cleanup_(dns_question_unrefp) DnsQuestion *question = make_question("localhost", DNS_TYPE_A);
                _cleanup_(dns_query_freep) DnsQuery *q = NULL;

                assert_se(dns_query_new(m, &q, question, question, 0, SD_RESOLVED_DNS) >= 0);
                assert_se(dns_query_go(q) == 1);
                assert_se(q->state == DNS_TRANSACTION_SUCCESS);
                assert_se(q->answer_rcode == DNS_RCODE_SUCCESS);
                assert_se(dns_answer_size(q->answer) > 0);
        }
}

static void test_search_and_transaction_reuse(Manager *m) {
        _cleanup_(dns_resource_key_unrefp) DnsResourceKey *key = NULL;
        _cleanup_(dns_transaction_freep) DnsTransaction *previous = NULL;
        _cleanup_(dns_question_unrefp) DnsQuestion *question = make_question("www", DNS_TYPE_A);
        _cleanup_(dns_query_freep) DnsQuery *q = NULL;

        assert_se(dns_search_domain_new(m, NULL, DNS_SEARCH_DOMAIN_SYSTEM, NULL, "facebook.com") >= 0);
        assert_se(key = dns_resource_key_new(DNS_CLASS_IN, DNS_TYPE_A, "www.facebook.com"));
        assert_se(dns_transaction_new(&previous, m->unicast_scope, key) >= 0);
        /* Simulate a completed positive transaction retained by another query across a reload. */
        previous->state = DNS_TRANSACTION_SUCCESS;
        previous->answer_rcode = DNS_RCODE_SUCCESS;
        previous->block_gc++;

        assert_se(dns_query_new(m, &q, question, question, 0, SD_RESOLVED_DNS) >= 0);
        assert_se(dns_query_go(q) == 1);
        assert_se(q->state == DNS_TRANSACTION_RCODE_FAILURE);
        assert_se(q->answer_rcode == DNS_RCODE_NXDOMAIN);
        assert_se(!q->answer_authenticated);
        assert_se(previous->state == DNS_TRANSACTION_SUCCESS);
        assert_se(!previous->sent);
        q = dns_query_free(q);
        previous = dns_transaction_free(previous);
        dns_search_domain_unlink_all(m->search_domains);

        /* Auxiliary lookups and retry entry points also stop before network I/O. */
        assert_se(dns_transaction_new(&previous, m->unicast_scope, key) >= 0);
        previous->block_gc++;
        assert_se(dns_transaction_go(previous) == 0);
        assert_se(previous->state == DNS_TRANSACTION_RCODE_FAILURE);
        assert_se(previous->answer_rcode == DNS_RCODE_NXDOMAIN);
        assert_se(previous->dns_udp_fd == -1);
        assert_se(!previous->sent);
}

typedef struct Upstream {
        unsigned queries;
} Upstream;

static int upstream_reply(sd_event_source *source, int fd, uint32_t revents, void *userdata) {
        _cleanup_(dns_packet_unrefp) DnsPacket *p = NULL, *reply = NULL;
        _cleanup_(dns_resource_record_unrefp) DnsResourceRecord *rr = NULL, *cname = NULL;
        struct sockaddr_in peer;
        socklen_t peer_size = sizeof(peer);
        Upstream *upstream = userdata;
        const char *name;
        ssize_t n;

        assert_se(dns_packet_new(&p, DNS_PROTOCOL_DNS, 4096, DNS_PACKET_SIZE_MAX) >= 0);
        n = recvfrom(fd, DNS_PACKET_DATA(p), p->allocated, 0, (struct sockaddr*) &peer, &peer_size);
        assert_se(n > 0);
        p->size = n;
        assert_se(dns_packet_extract(p) >= 0);
        upstream->queries++;
        name = dns_question_first_name(p->question);

        assert_se(dns_packet_new(&reply, DNS_PROTOCOL_DNS, 512, DNS_PACKET_SIZE_MAX) >= 0);
        assert_se(dns_packet_append_question(reply, p->question) >= 0);

        if (dns_name_equal(name, "alias.example") > 0) {
                assert_se(cname = dns_resource_record_new_full(DNS_CLASS_IN, DNS_TYPE_CNAME, name));
                assert_se(cname->cname.name = strdup("www.facebook.com"));
                cname->ttl = 60;
                assert_se(dns_packet_append_rr(reply, cname, 0, NULL, NULL) >= 0);
                name = cname->cname.name;
        } else if (dns_name_equal(name, "www.dname.example") > 0) {
                assert_se(cname = dns_resource_record_new_full(DNS_CLASS_IN, DNS_TYPE_DNAME, "dname.example"));
                assert_se(cname->dname.name = strdup("facebook.com"));
                cname->ttl = 60;
                assert_se(dns_packet_append_rr(reply, cname, 0, NULL, NULL) >= 0);
                name = "www.facebook.com";
        }

        assert_se(rr = dns_resource_record_new_full(DNS_CLASS_IN, DNS_TYPE_A, name));
        rr->ttl = 60;
        rr->a.in_addr.s_addr = htobe32(0xc0000201U); /* 192.0.2.1 */
        assert_se(dns_packet_append_rr(reply, rr, 0, NULL, NULL) >= 0);
        DNS_PACKET_HEADER(reply)->id = DNS_PACKET_HEADER(p)->id;
        DNS_PACKET_HEADER(reply)->flags = htobe16(DNS_PACKET_MAKE_FLAGS(1, 0, 0, 0, 1, 1, 0, 0, DNS_RCODE_SUCCESS));
        DNS_PACKET_HEADER(reply)->qdcount = htobe16(1);
        DNS_PACKET_HEADER(reply)->ancount = htobe16(cname ? 2 : 1);
        if (p->opt)
                assert_se(dns_packet_append_opt(reply, 4096, false, DNS_RCODE_SUCCESS, NULL) >= 0);
        assert_se(sendto(fd, DNS_PACKET_DATA(reply), reply->size, 0, (struct sockaddr*) &peer, peer_size) == (ssize_t) reply->size);
        return 0;
}

static void stub_stream_read(Manager *m, int fd, void *buffer, size_t size) {
        usec_t deadline = now(CLOCK_MONOTONIC) + 3 * USEC_PER_SEC;
        size_t received = 0;

        while (received < size) {
                ssize_t n;

                assert_se(sd_event_run(m->event, 100 * USEC_PER_MSEC) >= 0);
                n = recv(fd, (uint8_t*) buffer + received, size - received, 0);
                if (n > 0)
                        received += n;
                else
                        assert_se(n < 0 && errno == EAGAIN);
                assert_se(now(CLOCK_MONOTONIC) < deadline);
        }
}

static void test_stub_query_transport(Manager *m, const char *name, uint16_t type, int rcode, bool tcp) {
        _cleanup_close_ int fd = -1;
        _cleanup_(dns_question_unrefp) DnsQuestion *question = make_question(name, type);
        _cleanup_(dns_packet_unrefp) DnsPacket *p = NULL, *reply = NULL;
        const struct sockaddr_in stub = {
                .sin_family = AF_INET,
                .sin_port = htobe16(53),
                .sin_addr.s_addr = htobe32(INADDR_DNS_STUB),
        };
        usec_t deadline = now(CLOCK_MONOTONIC) + 3 * USEC_PER_SEC;
        ssize_t n;

        assert_se((fd = socket(AF_INET, (tcp ? SOCK_STREAM : SOCK_DGRAM)|SOCK_CLOEXEC, 0)) >= 0);
        assert_se(dns_packet_new_query(&p, DNS_PROTOCOL_DNS, 512, m->dnssec_mode != DNSSEC_NO) >= 0);
        assert_se(dns_packet_append_question(p, question) >= 0);
        DNS_PACKET_HEADER(p)->qdcount = htobe16(1);
        DNS_PACKET_HEADER(p)->id = htobe16(1234);
        assert_se(dns_packet_new(&reply, DNS_PROTOCOL_DNS, 4096, DNS_PACKET_SIZE_MAX) >= 0);

        if (tcp) {
                uint16_t size = htobe16(p->size);

                assert_se(connect(fd, (const struct sockaddr*) &stub, sizeof(stub)) == 0);
                assert_se(send(fd, &size, sizeof(size), MSG_NOSIGNAL) == sizeof(size));
                assert_se(send(fd, DNS_PACKET_DATA(p), p->size, MSG_NOSIGNAL) == (ssize_t) p->size);
                assert_se(fd_nonblock(fd, true) >= 0);
                stub_stream_read(m, fd, &size, sizeof(size));
                reply->size = be16toh(size);
                assert_se(reply->size <= reply->allocated);
                stub_stream_read(m, fd, DNS_PACKET_DATA(reply), reply->size);
        } else {
                assert_se(fd_nonblock(fd, true) >= 0);
                assert_se(sendto(fd, DNS_PACKET_DATA(p), p->size, 0, (const struct sockaddr*) &stub, sizeof(stub)) == (ssize_t) p->size);
                for (;;) {
                        assert_se(sd_event_run(m->event, 100 * USEC_PER_MSEC) >= 0);
                        n = recv(fd, DNS_PACKET_DATA(reply), reply->allocated, 0);
                        if (n >= 0)
                                break;
                        assert_se(errno == EAGAIN);
                        assert_se(now(CLOCK_MONOTONIC) < deadline);
                }
                reply->size = n;
        }

        assert_se(dns_packet_validate_reply(reply) > 0);
        assert_se(DNS_PACKET_ID(reply) == DNS_PACKET_ID(p));
        assert_se(DNS_PACKET_RCODE(reply) == rcode);
        assert_se(dns_packet_extract_full(reply, dns_type_is_valid_query(type)) >= 0);
        if (rcode == DNS_RCODE_FORMERR)
                assert_se(DNS_PACKET_QDCOUNT(reply) == 0);
        else
                assert_se(dns_question_is_equal(question, reply->question) > 0);
        if (rcode != DNS_RCODE_SUCCESS) {
                assert_se(DNS_PACKET_ANCOUNT(reply) == 0);
                assert_se(!DNS_PACKET_AD(reply));
        } else {
                assert_se(DNS_PACKET_ANCOUNT(reply) == 1);
                assert_se(dns_answer_size(reply->answer) == 1);
        }
}

static void test_stub_query(Manager *m, const char *name, uint16_t type, int rcode) {
        test_stub_query_transport(m, name, type, rcode, false);
        if (m->dns_stub_tcp_fd >= 0)
                test_stub_query_transport(m, name, type, rcode, true);
}

static void seed_positive_cache(Manager *m, const char *name) {
        _cleanup_(dns_resource_record_unrefp) DnsResourceRecord *rr = NULL;
        _cleanup_(dns_answer_unrefp) DnsAnswer *answer = NULL;
        const union in_addr_union owner = { .in.s_addr = htobe32(0xc0000235U) };

        /* v238 deliberately excludes replies from a loopback upstream from caching. Seed a normal remote
         * cache entry through its public API to exercise precedence without changing that behaviour. */
        assert_se(rr = dns_resource_record_new_full(DNS_CLASS_IN, DNS_TYPE_A, name));
        rr->ttl = 60;
        rr->a.in_addr.s_addr = htobe32(0xc0000201U);
        assert_se(dns_answer_add_extend(&answer, rr, 0, DNS_ANSWER_CACHEABLE) >= 0);
        assert_se(dns_cache_put(&m->unicast_scope->cache, rr->key, DNS_RCODE_SUCCESS, answer, false,
                               (uint32_t) -1, 0, AF_INET, &owner) >= 0);
}

static void test_stub(Manager *m, const char *path) {
        _cleanup_close_ int fd = -1;
        _cleanup_(sd_event_source_unrefp) sd_event_source *source = NULL;
        LinkAddress address = { .family = AF_INET, .scope = RT_SCOPE_UNIVERSE };
        Link link = {
                .manager = m,
                .ifindex = 999999,
                .mtu = 1500,
                .flags = IFF_UP|IFF_LOWER_UP,
                .operstate = IF_OPER_UP,
                .addresses = &address,
        };
        const struct sockaddr_in upstream_address = {
                .sin_family = AF_INET,
                .sin_port = htobe16(53),
                .sin_addr.s_addr = htobe32(0x7f000036U), /* 127.0.0.54 */
        };
        Upstream upstream = {};
        unsigned requests, cache_size;

        assert_se((fd = socket(AF_INET, SOCK_DGRAM|SOCK_CLOEXEC|SOCK_NONBLOCK, 0)) >= 0);
        if (bind(fd, (const struct sockaddr*) &upstream_address, sizeof(upstream_address)) < 0) {
                assert_se(IN_SET(errno, EACCES, EPERM, EADDRINUSE));
                log_notice("Skipping stub wire tests: cannot bind test upstream on 127.0.0.54:53.");
                return;
        }
        assert_se(manager_dns_stub_start(m) >= 0);
        if (m->dns_stub_udp_fd < 0) {
                log_notice("Skipping stub wire tests: local DNS stub is unavailable.");
                return;
        }
        if (m->dns_stub_tcp_fd < 0)
                log_notice("Skipping TCP wire tests: local TCP stub is unavailable.");

        assert_se(hashmap_ensure_allocated(&m->links, NULL) >= 0);
        assert_se(hashmap_put(m->links, INT_TO_PTR(link.ifindex), &link) >= 0);
        assert_se(sd_event_add_io(m->event, &source, fd, EPOLLIN, upstream_reply, &upstream) >= 0);
        test_stub_query(m, "facebook.com", DNS_TYPE_A, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "www.facebook.com", DNS_TYPE_AAAA, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "a.b.facebook.com", DNS_TYPE_TXT, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", DNS_TYPE_MX, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", 64, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", 65, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", DNS_TYPE_MD, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", DNS_TYPE_AXFR, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", DNS_TYPE_IXFR, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", DNS_TYPE_RRSIG, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", DNS_TYPE_OPT, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", DNS_TYPE_TSIG, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", DNS_TYPE_TKEY, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", 0, DNS_RCODE_NXDOMAIN);
        assert_se(upstream.queries == 0);

        /* Local denials also precede DNSSEC processing, and never claim authenticated data. */
        m->dnssec_mode = m->unicast_scope->dnssec_mode = DNSSEC_YES;
        test_query_policy(m);
        test_search_and_transaction_reuse(m);
        test_stub_query(m, "facebook.com", DNS_TYPE_A, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "facebook.com", DNS_TYPE_DNSKEY, DNS_RCODE_NXDOMAIN);
        assert_se(upstream.queries == 0);
        m->dnssec_mode = m->unicast_scope->dnssec_mode = DNSSEC_NO;
        test_stub_query(m, "unblocked.example", DNS_TYPE_MD, DNS_RCODE_NOTIMP);
        test_stub_query(m, "unblocked.example", DNS_TYPE_RRSIG, DNS_RCODE_FORMERR);

        test_stub_query(m, "notfacebook.com", DNS_TYPE_A, DNS_RCODE_SUCCESS);
        test_stub_query(m, "facebook.com.example.org", DNS_TYPE_A, DNS_RCODE_SUCCESS);
        assert_se(upstream.queries >= 2);
        requests = upstream.queries;
        seed_positive_cache(m, "notfacebook.com");
        test_stub_query(m, "notfacebook.com", DNS_TYPE_A, DNS_RCODE_SUCCESS);
        assert_se(upstream.queries == requests); /* ordinary cached answers still work */

        /* A CNAME reply that includes a positive target RR cannot bypass the blocked target. */
        test_stub_query(m, "alias.example", DNS_TYPE_A, DNS_RCODE_NXDOMAIN);
        test_stub_query(m, "www.dname.example", DNS_TYPE_A, DNS_RCODE_NXDOMAIN);
        requests = upstream.queries;
        cache_size = dns_cache_size(&m->unicast_scope->cache);
        assert_se(cache_size > 0);

        assert_se(write_string_file(path, "facebook.com\nnotfacebook.com", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(dns_blocklist_reload(m->blocked_domain_files, false, &m->blocked_domains) >= 0);
        assert_se(dns_cache_size(&m->unicast_scope->cache) == cache_size);
        test_stub_query(m, "notfacebook.com", DNS_TYPE_A, DNS_RCODE_NXDOMAIN);
        assert_se(upstream.queries == requests); /* the old positive cache entry cannot bypass a reload */

        assert_se(write_string_file(path, "", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(dns_blocklist_reload(m->blocked_domain_files, false, &m->blocked_domains) >= 0);
        test_stub_query(m, "notfacebook.com", DNS_TYPE_A, DNS_RCODE_SUCCESS);
        assert_se(upstream.queries == requests); /* unblocking reveals the untouched ordinary cache */
        test_stub_query(m, "unblocked.example", DNS_TYPE_RRSIG, DNS_RCODE_FORMERR);

        assert_se(hashmap_remove(m->links, INT_TO_PTR(link.ifindex)) == &link);
        log_info("Stub NXDOMAIN, upstream, CNAME/DNAME, DNSSEC policy and cache tests passed (TCP %s).",
                 m->dns_stub_tcp_fd >= 0 ? "enabled" : "skipped");
        manager_dns_stub_stop(m);
}

int main(int argc, char **argv) {
        char path[] = "/tmp/test-resolved-blocklist-XXXXXX";
        _cleanup_close_ int fd = -1;
        const union in_addr_union upstream = { .in.s_addr = htobe32(0x7f000036U) };
        Manager m = {
                .dnssec_mode = DNSSEC_NO,
                .enable_cache = true,
                .dns_stub_listener_mode = DNS_STUB_LISTENER_YES,
                .dns_stub_udp_fd = -1,
                .dns_stub_tcp_fd = -1,
                .etc_hosts_mtime = USEC_INFINITY,
                .full_hostname = (char*) "test-host",
                .llmnr_hostname = (char*) "test-host",
                .mdns_hostname = (char*) "test-host",
        };

        log_set_max_level(getenv("SYSTEMD_BLOCKLIST_TEST_DEBUG") ? LOG_DEBUG : LOG_INFO);
        assert_se((fd = mkostemp_safe(path)) >= 0);
        assert_se(write_string_file(path, "facebook.com", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(sd_event_new(&m.event) >= 0);
        assert_se(sd_event_now(m.event, clock_boottime_or_monotonic(), &m.etc_hosts_last) >= 0);
        assert_se(dns_scope_new(&m, &m.unicast_scope, NULL, DNS_PROTOCOL_DNS, AF_UNSPEC) >= 0);
        assert_se(dns_server_new(&m, NULL, DNS_SERVER_SYSTEM, NULL, AF_INET, &upstream, 0) >= 0);
        assert_se(manager_set_dns_server(&m, m.dns_servers));

        test_config(&m, path);
        assert_se(dns_blocklist_reload(m.blocked_domain_files, true, &m.blocked_domains) >= 0);
        test_query_policy(&m);
        test_search_and_transaction_reuse(&m);
        test_stub(&m, path);

        assert_se(m.n_dns_queries == 0);
        assert_se(m.n_dns_streams == 0);
        manager_dns_stub_stop(&m);
        dns_scope_free(m.unicast_scope);
        dns_server_unlink_all(m.dns_servers);
        dns_server_unref(m.current_dns_server);
        hashmap_free(m.links);
        hashmap_free(m.dns_transactions);
        manager_etc_hosts_flush(&m);
        strv_free(m.blocked_domain_files);
        set_free_free(m.blocked_domains);
        sd_event_unref(m.event);
        assert_se(unlink(path) == 0);
        return 0;
}
