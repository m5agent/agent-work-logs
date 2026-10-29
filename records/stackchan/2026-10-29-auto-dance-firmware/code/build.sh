#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cli=${ARDUINO_CLI:-arduino-cli}

run_cli() {
    if [ -n "${ARDUINO_CONFIG_FILE:-}" ]; then
        "$cli" --config-file "$ARDUINO_CONFIG_FILE" "$@"
    else
        "$cli" "$@"
    fi
}

python3 "$root/tools/validate_timeline.py"
mkdir -p "$root/build/arduino" "$root/build/arduino-build"

run_cli compile \
    --fqbn m5stack:esp32:m5stack_cores3 \
    --build-path "$root/build/arduino-build" \
    --output-dir "$root/build/arduino" \
    --export-binaries \
    --warnings default \
    "$root/stackchan_dance"

printf '%s\n' "Built: $root/build/arduino/stackchan_dance.ino.merged.bin"
