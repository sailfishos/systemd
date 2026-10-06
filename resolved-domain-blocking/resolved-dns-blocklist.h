/* SPDX-License-Identifier: LGPL-2.1+ */
#pragma once

#include <stdbool.h>

#include "set.h"

/* On failure, the active set is left untouched. Only startup may ignore missing files. */
int dns_blocklist_reload(char **files, bool ignore_missing, Set **active);
bool dns_blocklist_contains(Set *domains, const char *name);
