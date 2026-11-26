#!/usr/bin/env bash
set -euo pipefail
sim=$ESP32SIM_P4
rom=$ESP32SIM_ROM_DIR
fw=$1
out=$2
mkdir "$out"
printf '%s\n' '7.0 touch 83 755 1' '7.45 touch 83 755 0' >"$out/touch.txt"
c6="c6:bootloader=$fw/c6-bootloader.bin,ptable=$fw/c6-partitions.bin,otadata=$fw/c6-otadata.bin,app=$fw/c6-app.bin"
for version in 3 4; do
    for action in home adc; do
        prefix="$out/25${version}-$action"
        flags=(--debug dma2d,ppa,dsi)
        if [[ "$action" == adc ]]; then
            flags=(--script "$out/touch.txt" --debug i2c1 --wav "$prefix.wav")
        fi
        "$sim" --board m5stack-tab5 --boot rom --rom "$rom/esp32p4_rev0_rom.elf" \
            --flash-image "$fw/uiflow2-v2.5.$version.bin" --max-seconds 9 --console both \
            --no-dump --tft-png "$prefix.png" --coproc "$c6" "${flags[@]}" \
            >"$prefix.console.log" 2>"$prefix.model.log"
    done
done
