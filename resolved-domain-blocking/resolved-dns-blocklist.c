/* SPDX-License-Identifier: LGPL-2.1+ */

#include <fcntl.h>
#include <sys/stat.h>

#include "alloc-util.h"
#include "dns-domain.h"
#include "fd-util.h"
#include "log.h"
#include "resolved-dns-blocklist.h"
#include "string-util.h"
#include "strv.h"

#define BLOCKLIST_BYTES_MAX (64U * 1024U * 1024U)
#define BLOCKLIST_DOMAINS_MAX (1024U * 1024U)
#define BLOCKLIST_LINE_MAX 4096U

static int dns_blocklist_read_line(FILE *f, char *line) {
        unsigned n;

        /* Unlike v238's read_line(), reject embedded NULs, including in comments. The stream is private
         * to this loader, and the caller reuses a bounded buffer instead of allocating for every line. */
        for (n = 0; n < BLOCKLIST_LINE_MAX; n++) {
                int c;

                errno = 0;
                c = getc_unlocked(f);
                if (c == EOF) {
                        if (ferror(f))
                                return errno > 0 ? -errno : -EIO;
                        line[n] = 0;
                        return n;
                }
                if (c == 0)
                        return -EBADMSG;
                if (c == '\n') {
                        line[n] = 0;
                        return n + 1;
                }
                line[n] = c;
        }

        return -ENOBUFS;
}

static int dns_blocklist_load_file(const char *path, bool ignore_missing, Set *domains, size_t *bytes) {
        _cleanup_fclose_ FILE *f = NULL;
        _cleanup_close_ int fd = -1;
        struct stat before, after;
        char line[BLOCKLIST_LINE_MAX];
        unsigned line_number = 0, valid = 0, invalid = 0;
        int r;

        assert(path);
        assert(domains);
        assert(bytes);

        fd = open(path, O_RDONLY|O_CLOEXEC|O_NONBLOCK|O_NOCTTY);
        if (fd < 0) {
                r = -errno;
                log_warning_errno(r, "Failed to open blocked domain file %s: %m", path);
                return ignore_missing && r == -ENOENT ? 0 : r;
        }

        if (fstat(fd, &before) < 0)
                return log_warning_errno(errno, "Failed to stat blocked domain file %s: %m", path);
        if (!S_ISREG(before.st_mode))
                return log_warning_errno(EINVAL, "Blocked domain file %s is not a regular file.", path);
        if (before.st_size < 0 || (uint64_t) before.st_size > BLOCKLIST_BYTES_MAX - *bytes)
                return log_warning_errno(E2BIG, "Blocked domain files exceed the %u byte limit.", BLOCKLIST_BYTES_MAX);

        f = fdopen(fd, "r");
        if (!f)
                return log_warning_errno(errno, "Failed to read blocked domain file %s: %m", path);
        fd = -1;

        for (;;) {
                _cleanup_free_ char *normalized = NULL;
                const char *name;

                r = dns_blocklist_read_line(f, line);
                if (r < 0)
                        return log_warning_errno(r, "Failed to read blocked domain file %s: %m", path);
                if (r == 0)
                        break;
                if ((size_t) r > BLOCKLIST_BYTES_MAX - *bytes)
                        return log_warning_errno(E2BIG, "Blocked domain files exceed the %u byte limit.", BLOCKLIST_BYTES_MAX);
                *bytes += r;
                line_number++;

                name = strstrip(line);
                if (isempty(name) || name[0] == '#')
                        continue;

                /* DNS presentation names are more permissive than this file format. In particular, do not
                 * accidentally accept a hosts entry, URL, wildcard or common ad-block expression as a name. */
                r = strpbrk(name, WHITESPACE "/*:?[]|#^$(){}+") ? -EINVAL : dns_name_normalize(name, &normalized);
                if (r == -ENOMEM)
                        return r;
                if (r < 0 || dns_name_is_root(normalized)) {
                        if (invalid++ < 10)
                                log_warning("%s:%u: Ignoring malformed blocked domain: %s", path, line_number, name);
                        continue;
                }

                valid++;
                if (set_contains(domains, normalized))
                        continue;
                if (set_size(domains) >= BLOCKLIST_DOMAINS_MAX)
                        return log_warning_errno(E2BIG, "Blocked domain files exceed the %u domain limit.", BLOCKLIST_DOMAINS_MAX);

                r = set_put(domains, normalized);
                if (r < 0)
                        return r;
                normalized = NULL;
        }

        if (ferror(f))
                return log_warning_errno(EIO, "Failed to read blocked domain file %s.", path);
        if (fstat(fileno(f), &after) < 0)
                return log_warning_errno(errno, "Failed to stat blocked domain file %s: %m", path);
        if (before.st_size != after.st_size ||
            before.st_mtim.tv_sec != after.st_mtim.tv_sec || before.st_mtim.tv_nsec != after.st_mtim.tv_nsec ||
            before.st_ctim.tv_sec != after.st_ctim.tv_sec || before.st_ctim.tv_nsec != after.st_ctim.tv_nsec)
                return log_warning_errno(ESTALE, "Blocked domain file %s changed while reading it.", path);

        if (invalid > 10)
                log_warning("%s: Ignored %u malformed blocked domains.", path, invalid);
        if (!ignore_missing && invalid > 0 && valid == 0)
                return log_warning_errno(EINVAL, "Blocked domain file %s has no valid entries. Keeping the active lists.", path);

        return 0;
}

int dns_blocklist_reload(char **files, bool ignore_missing, Set **active) {
        _cleanup_set_free_free_ Set *domains = NULL;
        Set *old;
        size_t bytes = 0;
        char **file;
        int r;

        assert(active);

        if (!strv_isempty(files)) {
                domains = set_new(&dns_name_hash_ops);
                if (!domains)
                        return -ENOMEM;

                STRV_FOREACH(file, files) {
                        r = dns_blocklist_load_file(*file, ignore_missing, domains, &bytes);
                        if (r < 0)
                                return r;
                }
        }

        /* Parsing is synchronous in resolved's event loop. No query can observe an intermediate set. */
        old = *active;
        *active = domains;
        domains = NULL;
        set_free_free(old);

        log_debug("Loaded %u blocked DNS domains.", set_size(*active));
        return 0;
}

bool dns_blocklist_contains(Set *domains, const char *name) {
        int r;

        if (set_isempty(domains) || !name)
                return false;

        /* Advancing through parsed DNS labels also handles escaped dots correctly. The DNS hash operations
         * compare case-insensitively and treat a trailing root dot as equivalent. */
        while (!dns_name_is_root(name)) {
                if (set_contains(domains, name))
                        return true;

                r = dns_name_parent(&name);
                if (r <= 0)
                        break;
        }

        return false;
}
