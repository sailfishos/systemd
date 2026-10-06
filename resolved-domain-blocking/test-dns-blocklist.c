/* SPDX-License-Identifier: LGPL-2.1+ */

#include <fcntl.h>
#include <unistd.h>

#include "alloc-util.h"
#include "fd-util.h"
#include "fileio.h"
#include "log.h"
#include "resolved-dns-blocklist.h"
#include "string-util.h"

static void test_load_and_match(const char *first, const char *second) {
        _cleanup_set_free_free_ Set *domains = NULL;
        char *files[] = { (char*) first, (char*) second, NULL };

        assert_se(write_string_file(first,
                                   "  # comment\n\n\t\r\n Facebook.COM. \t\r\nfacebook.com\n"
                                   "example..org\n.example.org\n.\n*.example.org\n"
                                   "https://example.org\n0.0.0.0 example.org\n||example.org^\n"
                                   "bad\\escape.org\nexample.org # inline comment\n"
                                   "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com\n"
                                   "other.example.org\n",
                                   WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(write_string_file(second, "advertising.example\nsocial.example\r\nFACEBOOK.com.",
                                   WRITE_STRING_FILE_CREATE|WRITE_STRING_FILE_AVOID_NEWLINE) >= 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == 0);
        assert_se(set_size(domains) == 4);

        assert_se(dns_blocklist_contains(domains, "facebook.com"));
        assert_se(dns_blocklist_contains(domains, "www.facebook.com"));
        assert_se(dns_blocklist_contains(domains, "graph.facebook.com"));
        assert_se(dns_blocklist_contains(domains, "foo.bar.facebook.com"));
        assert_se(dns_blocklist_contains(domains, "WWW.FaCeBoOk.cOm."));
        assert_se(dns_blocklist_contains(domains, "a\\.b.facebook.com"));
        assert_se(dns_blocklist_contains(domains, "www.advertising.example"));
        assert_se(dns_blocklist_contains(domains, "social.example."));
        assert_se(!dns_blocklist_contains(domains, "notfacebook.com"));
        assert_se(!dns_blocklist_contains(domains, "facebook.com.example.org"));
        assert_se(!dns_blocklist_contains(domains, "facebook\\.com"));
        assert_se(!dns_blocklist_contains(domains, "www.example.org"));
        assert_se(!dns_blocklist_contains(domains, "."));
        assert_se(!dns_blocklist_contains(domains, NULL));
        assert_se(!dns_blocklist_contains(NULL, "facebook.com"));
}

static void test_reload(const char *first, const char *second) {
        _cleanup_set_free_free_ Set *domains = NULL;
        char *files[] = { (char*) first, (char*) second, NULL };
        Set *old;

        assert_se(write_string_file(first, "old.example", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(write_string_file(second, "shared.example", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == 0);
        assert_se(dns_blocklist_contains(domains, "old.example"));
        old = domains;

        /* One new list plus one missing list must never install the partial result. */
        assert_se(write_string_file(first, "new.example", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(unlink(second) == 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == -ENOENT);
        assert_se(domains == old);
        assert_se(dns_blocklist_contains(domains, "old.example"));
        assert_se(dns_blocklist_contains(domains, "shared.example"));
        assert_se(!dns_blocklist_contains(domains, "new.example"));

        /* A file containing only malformed entries also cannot accidentally disable an existing list. */
        assert_se(write_string_file(second, "bad..example\n*.example", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == -EINVAL);
        assert_se(domains == old);

        assert_se(write_string_file(second, "replacement.example", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == 0);
        assert_se(dns_blocklist_contains(domains, "new.example"));
        assert_se(dns_blocklist_contains(domains, "replacement.example"));
        assert_se(!dns_blocklist_contains(domains, "old.example"));
        assert_se(!dns_blocklist_contains(domains, "shared.example"));

        /* Empty/comment-only files intentionally clear the policy. */
        assert_se(write_string_file(first, "# now empty", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(write_string_file(second, "", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == 0);
        assert_se(set_isempty(domains));

        assert_se(write_string_file(first, "startup.example", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(unlink(second) == 0);
        assert_se(dns_blocklist_reload(files, true, &domains) == 0);
        assert_se(dns_blocklist_contains(domains, "startup.example"));
        assert_se(dns_blocklist_reload(NULL, false, &domains) == 0);
        assert_se(domains == NULL);
}

static void test_binary_reload(const char *first, const char *second) {
        _cleanup_set_free_free_ Set *domains = NULL;
        char *files[] = { (char*) first, (char*) second, NULL };
        static const char zeroes[4096] = {};
        static const char utf16[] = "f\0a\0c\0e\0b\0o\0o\0k\0.\0c\0o\0m\0\n\0";
        static const char mixed[] = "partial.example\nfacebook.com\0other.example\n";
        static const char comment[] = "# comment\0hidden.example\n";
        static const struct {
                const char *data;
                size_t size;
        } cases[] = {
                { zeroes, sizeof(zeroes) },
                { utf16, sizeof(utf16) - 1 },
                { mixed, sizeof(mixed) - 1 },
                { comment, sizeof(comment) - 1 },
        };
        Set *old;
        unsigned i;

        assert_se(write_string_file(first, "old.example", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(write_string_file(second, "facebook.com", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == 0);
        old = domains;
        assert_se(write_string_file(first, "new.example", WRITE_STRING_FILE_CREATE) >= 0);

        for (i = 0; i < ELEMENTSOF(cases); i++) {
                _cleanup_fclose_ FILE *f = NULL;
                _cleanup_set_free_free_ Set *startup = NULL;

                assert_se(f = fopen(second, "we"));
                assert_se(fwrite(cases[i].data, 1, cases[i].size, f) == cases[i].size);
                assert_se(fflush(f) == 0);
                assert_se(dns_blocklist_reload(files, false, &domains) == -EBADMSG);
                assert_se(domains == old);
                assert_se(set_size(domains) == 2);
                assert_se(dns_blocklist_contains(domains, "old.example"));
                assert_se(dns_blocklist_contains(domains, "facebook.com"));
                assert_se(!dns_blocklist_contains(domains, "new.example"));

                /* Startup skips missing files, but must still reject corrupt input as a whole. */
                assert_se(dns_blocklist_reload(files, true, &startup) == -EBADMSG);
                assert_se(!startup);
        }

        assert_se(unlink(second) == 0);
}

static void test_limits(const char *path, const char *directory) {
        _cleanup_set_free_free_ Set *domains = NULL;
        _cleanup_close_ int fd = -1;
        char *files[] = { (char*) path, NULL };
        char *directories[] = { (char*) directory, NULL };
        char long_line[4098];
        Set *old;

        assert_se(write_string_file(path, "retained.example", WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == 0);
        old = domains;

        memset(long_line, 'a', sizeof(long_line) - 1);
        long_line[sizeof(long_line) - 1] = 0;
        assert_se(write_string_file(path, long_line, WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == -ENOBUFS);
        assert_se(domains == old);

        fd = open(path, O_WRONLY|O_CLOEXEC);
        assert_se(fd >= 0);
        assert_se(ftruncate(fd, 64U * 1024U * 1024U + 1) == 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == -E2BIG);
        assert_se(domains == old);
        assert_se(dns_blocklist_reload(directories, false, &domains) == -EINVAL);
        assert_se(domains == old);
        assert_se(dns_blocklist_contains(domains, "retained.example"));

        /* The maximum accepted line length is the same with and without a final newline. */
        memset(long_line, ' ', 4095);
        memcpy(long_line, "boundary.example", STRLEN("boundary.example"));
        long_line[4095] = 0;
        assert_se(write_string_file(path, long_line, WRITE_STRING_FILE_CREATE|WRITE_STRING_FILE_AVOID_NEWLINE) >= 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == 0);
        assert_se(dns_blocklist_contains(domains, "boundary.example"));
        assert_se(write_string_file(path, long_line, WRITE_STRING_FILE_CREATE) >= 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == 0);
        assert_se(dns_blocklist_contains(domains, "boundary.example"));
}

static void test_large_list(const char *path) {
        _cleanup_set_free_free_ Set *domains = NULL;
        _cleanup_fclose_ FILE *f = NULL;
        char *files[] = { (char*) path, NULL };
        unsigned i;

        assert_se(f = fopen(path, "we"));
        for (i = 0; i < 100000; i++)
                assert_se(fprintf(f, "entry%u.example\n", i) > 0);
        assert_se(fflush(f) == 0);
        assert_se(dns_blocklist_reload(files, false, &domains) == 0);
        assert_se(set_size(domains) == 100000);
        assert_se(dns_blocklist_contains(domains, "a.b.entry0.example"));
        assert_se(dns_blocklist_contains(domains, "a.b.entry99999.example"));
        assert_se(!dns_blocklist_contains(domains, "entry100000.example"));
}

int main(int argc, char **argv) {
        char directory[] = "/tmp/test-dns-blocklist-XXXXXX";
        _cleanup_free_ char *first = NULL, *second = NULL;

        log_set_max_level(LOG_INFO);
        assert_se(mkdtemp(directory));
        assert_se(first = strjoin(directory, "/first", NULL));
        assert_se(second = strjoin(directory, "/second", NULL));

        test_load_and_match(first, second);
        test_reload(first, second);
        test_binary_reload(first, second);
        test_limits(first, directory);
        test_large_list(first);

        assert_se(unlink(first) == 0);
        assert_se(rmdir(directory) == 0);
        return 0;
}
