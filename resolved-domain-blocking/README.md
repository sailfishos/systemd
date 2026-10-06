# DNS domain blocking

Add lists to `/etc/systemd/resolved.conf` or a drop-in:

```ini
[Resolve]
BlockedDomainFile=/var/lib/dns-policy/blocked.domains
```

Repeat the setting for multiple files; an empty assignment resets the paths.
Files must be readable by `systemd-resolve` and contain one domain suffix per
line, with optional blank lines and `#` comments:

```text
ads.example
tracking.example
```

Entries match the domain and its subdomains, ignoring case and trailing dots.
Use plain domain lists, not hosts-file or Adblock syntax. Blocked names return
unauthenticated NXDOMAIN before hosts/cache lookup, including alias targets
and search-domain expansions. No lists configured means no blocking.

After replacing list files by atomic rename, reload as root:

```sh
busctl call org.freedesktop.resolve1 /org/freedesktop/resolve1 \
    org.freedesktop.resolve1.Manager ReloadBlockLists
```

Failed reloads retain the old lists; empty files remove their entries. Malformed
lines are skipped, but wholly malformed files fail reload. Binary input is
rejected. Reloading preserves DNS caches; changing configured paths requires a
service restart. At startup, missing files are skipped and other load failures
leave blocking disabled.

Limits: 64 files, 64 MiB total input, 1,048,576 distinct suffixes and lines shorter
than 4096 bytes.
