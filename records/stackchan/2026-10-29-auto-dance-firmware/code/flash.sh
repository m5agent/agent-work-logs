#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
port=${1:-}
tool=${ESPTOOL:-esptool}
image="$root/build/arduino/stackchan_dance.ino.merged.bin"

if [ -z "$port" ]; then
    printf 'Usage: %s /dev/cu.usbmodemXXXX\n' "$0" >&2
    exit 64
fi
if [ ! -f "$image" ]; then
    printf 'Missing firmware image: %s\n' "$image" >&2
    exit 66
fi

"$tool" --chip esp32s3 --port "$port" --baud 921600 \
    write_flash --flash-mode dio --flash-frequency 80m --flash-size 16MB \
    0x000000 "$image"
