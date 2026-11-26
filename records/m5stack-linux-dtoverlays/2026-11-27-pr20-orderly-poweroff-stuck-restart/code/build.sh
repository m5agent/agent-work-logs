#!/usr/bin/env bash
# Rebuild the host-level harness for modules/CardputerZero/powerfail_suo.c
# (m5stack-linux-dtoverlays PR #20 head 3b6d273). No kernel tree needed.
# The driver source is compiled unchanged against stub headers.
set -eu
cd "$(dirname "$0")"
CFLAGS="-std=gnu11 -O1 -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -Wno-unused-function -I stub"
clang $CFLAGS -o harness harness.c
./harness
