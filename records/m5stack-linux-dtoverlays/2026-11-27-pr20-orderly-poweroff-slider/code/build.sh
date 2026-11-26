#!/usr/bin/env bash
# Rebuild the host-level harness for modules/CardputerZero/powerfail_suo.c.
# No kernel tree needed: stub/ contains the kernel APIs the driver uses.
set -eu
cd "$(dirname "$0")"
CFLAGS="-std=gnu11 -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -I stub"

clang $CFLAGS -o harness harness.c
clang $CFLAGS -DFIXED_BUILD -DDRIVER_SRC='"powerfail_suo_fixed.c"' -o harness_fixed harness.c

./harness
./harness_fixed
