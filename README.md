## Packaging guide

**All changes go to rpm/systemd.spec !**

To update rpm/systemd-mini.spec run

    ./precheckin.sh

The downstream DNS blocking module, tests and documentation live in
[resolved-domain-blocking/](resolved-domain-blocking/README.md). RPM preparation
symlinks the new source files into systemd; its integration patch changes only
existing upstream files.
