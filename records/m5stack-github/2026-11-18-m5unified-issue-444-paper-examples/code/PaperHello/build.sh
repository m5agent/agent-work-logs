#!/usr/bin/env bash
# Build only (no upload). Requires arduino-cli with the esp32 core installed,
# plus M5Unified and M5GFX checkouts:
#
#   arduino-cli core install esp32:esp32
#   M5UNIFIED_PATH=~/M5Unified M5GFX_PATH=~/M5GFX ./build.sh
#
# This sketch was not compiled in the 2026-11-18 run (host had no toolchain).
set -euo pipefail
cd "$(dirname "$0")"
: "${M5UNIFIED_PATH:?set M5UNIFIED_PATH to the M5Unified checkout}"
: "${M5GFX_PATH:?set M5GFX_PATH to the M5GFX checkout}"

arduino-cli compile \
  --fqbn esp32:esp32:m5stack_paper \
  --libraries "$M5UNIFIED_PATH" \
  --libraries "$M5GFX_PATH" \
  .
