#!/bin/bash
set -eo pipefail
root=$(cd "$(dirname "$0")" && pwd)
bin=${ESP32SIM_P4:?set ESP32SIM_P4 to the esp32sim-p4 executable}
rom=${ESP32SIM_ROM_DIR:?set ESP32SIM_ROM_DIR to the ROM directory}
board=${1:?board name}
name=${2:?run label}
firmware=${3:?merged image}
seconds=${4:-5}
shift "$(( $# < 4 ? $# : 4 ))"
out="$root/runs/$name"
mkdir -p "$out"
shasum -a 256 "$firmware" "$bin" "$rom/esp32p4_rev0_rom.elf" > "$out/sha256"
timeout_args=(--timeout 150s)
for arg in "$@"; do
  if [[ "$arg" == --coproc ]]; then timeout_args=(); fi
done
"$bin" --board "$board" --boot rom --rom "$rom/esp32p4_rev0_rom.elf" --flash-image "$firmware" \
  --max-seconds "$seconds" "${timeout_args[@]}" --console both --no-dump --tft-png "$out/frame.png" "$@" > "$out/console.log" 2> "$out/model.log"
