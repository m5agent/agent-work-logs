#!/bin/sh
# Compile the M5GFX board_detect sources against the host I/O stub and run the
# snapshot-restore equivalence checks.
#   usage: M5GFX_SRC=/path/to/M5GFX ./run.sh
set -eu
src=${M5GFX_SRC:?set M5GFX_SRC to a clean M5GFX checkout}
here=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
cxx=${CXX:-c++}
tmp=$(mktemp -d "${TMPDIR:-/tmp}/m5gfx-pr422.XXXXXX")
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

common="-std=gnu++17 -Wall -Wextra -fsyntax-only"
inc="-I$src/src -I$here"
def='-DM5GFX_BOARD_DETECT_IO_HEADER="stub_io.hpp"'

echo "===== log arguments compiled out (CORE_DEBUG_LEVEL=0 equivalent) ====="
# shellcheck disable=SC2086
$cxx $common $inc $def "$here/tu.cpp" 2>&1 || true

echo
echo "===== ESP_LOGD enabled (arguments evaluated) ====="
# shellcheck disable=SC2086
$cxx $common $inc $def -DHM_LOG_LEVEL=4 "$here/tu.cpp" 2>&1 || true

echo
echo "===== snapshot restore equivalence (log capture) ====="
# shellcheck disable=SC2086
$cxx -std=gnu++17 -Wall -Wextra -Wno-format-security -DHM_LOG_CAPTURE \
  $inc $def "$here/tx_check.cpp" -o "$tmp/tx_check"
"$tmp/tx_check"
