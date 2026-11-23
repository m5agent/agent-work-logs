#!/usr/bin/env bash
# Reproduce M5Cardputer-UserDemo #48 round 3: build CardputerADV with ESP-IDF v6.1.
# Writes only under /tmp; does not modify upstream or any installed IDF.
set -euo pipefail

IDF_61_DIR="${IDF_61_DIR:-$HOME/Documents/esp-idf-6.1}"
WORK="${WORK:-/tmp/cpadv48}"
BRANCH=CardputerADV

[ -d "$IDF_61_DIR" ] || { echo "ESP-IDF 6.1 checkout not found at $IDF_61_DIR"; exit 1; }
[ -x "$IDF_61_DIR/export.sh" ] || { echo "no export.sh in $IDF_61_DIR"; exit 1; }

rm -rf "$WORK"
git clone --depth 1 -b "$BRANCH" https://github.com/m5stack/M5Cardputer-UserDemo.git "$WORK"
cd "$WORK"
git log -1 --format='%H %cI %s'

# Project components (M5GFX, M5Unified, mooncake, mooncake_log, smooth_ui_toolkit)
python3 ./fetch_repos.py
ls components

# shellcheck disable=SC1091
. "$IDF_61_DIR/export.sh"
idf.py --version

echo "== attempt 1: untouched tree (expected: usb component resolution fails) =="
idf.py build || echo "attempt 1 failed as expected"

echo "== attempt 2: add espressif/usb, rebuild (expected: M5GFX lgfx_qrcode.h C23 bool) =="
idf.py add-dependency espressif/usb
rm -rf build sdkconfig
idf.py build || echo "attempt 2 failed as expected"
