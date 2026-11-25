#!/bin/sh
# Build and run the PoE-P4X revision-gate host probe against an M5GFX checkout.
# Usage: ./build_and_run.sh /path/to/M5GFX-at-PR-head
set -eu
tree=${1:?usage: build_and_run.sh <M5GFX checkout>}
here=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
out=$(mktemp -d "${TMPDIR:-/tmp}/poep4x-gate.XXXXXX")
trap 'rm -rf "$out"' EXIT HUP INT TERM
"${CXX:-c++}" -std=c++11 -O2 -Wall -Wextra -Wno-unused-function \
  -Wno-unused-parameter -pedantic \
  '-DM5GFX_BOARD_DETECT_IO_HEADER="support/detect_io.hpp"' \
  -include "$tree/test/board_detect/support/native_devices_io.hpp" \
  -I"$tree/test/board_detect" -I"$tree/test/board_detect/stubs" -I"$tree/src" \
  "$here/poep4x_gate_probe.cpp" -o "$out/probe"
"$out/probe"
