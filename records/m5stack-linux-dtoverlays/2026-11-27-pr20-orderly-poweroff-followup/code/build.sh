#!/usr/bin/env bash
# Rebuild the host-level harness for modules/CardputerZero/powerfail_suo.c
# (m5stack-linux-dtoverlays PR #20 head ff4cd84). No kernel tree needed.
# The second binary applies the backstop-restart proposal kept in
# powerfail_suo_proposed.c; only T25 changes behaviour.
set -eu
cd "$(dirname "$0")"
CFLAGS="-std=gnu11 -O1 -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -Wno-unused-function -I stub"

clang $CFLAGS -o harness harness.c
clang $CFLAGS -DPROPOSED_BUILD -DDRIVER_SRC='"powerfail_suo_proposed.c"' -o harness_proposed harness.c

./harness
./harness_proposed
