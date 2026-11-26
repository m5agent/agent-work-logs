#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
c6=${TAB5_C6_WLAN_BUILD:?set TAB5_C6_WLAN_BUILD to the ESP-Hosted 2.0.13 SDIO slave build directory}
coproc="c6:bootloader=$c6/bootloader/bootloader.bin,ptable=$c6/partition_table/partition-table.bin,otadata=$c6/ota_data_initial.bin,app=$c6/network_adapter.bin,elf=$c6/network_adapter.elf,stub=bb_init=0"
ap=$(python3 - <<'PY'
from pathlib import Path
import re
s = Path("firmware/wifi-1/sketch/sketch.ino").read_text()
ssid, password = [re.search(r'\b' + name + r'\s*=\s*"([^"]*)"', s)[1] for name in ("ssid", "password")]
assert (ssid, password) == ("ssid", "password"), "expected the published example placeholder AP values"
print(f"ssid={ssid},psk={password}")
PY
)
./run_tab5.sh m5stack-tab5 tab5-wifi-ap firmware/wifi-1/sketch.ino.merged.bin 10 --coproc "$coproc" --wifi "$ap" --net nat --debug net &
sta=$!
./run_tab5.sh m5stack-tab5 tab5-scan-ap firmware/wifi-2/sketch.ino.merged.bin 9 --coproc "$coproc" --wifi "$ap" --net none --debug net &
scan=$!
./run_tab5.sh m5stack-tab5 tab5-sntp-ap firmware/rtc-2/sketch.ino.merged.bin 18 --coproc "$coproc" --wifi "$ap" --net none,epoch=1764150000 --debug net,i2c1 &
sntp=$!
./run_tab5.sh m5stack-tab5 tab5-softap wifi-ap/build/sketch.ino.merged.bin 10 --coproc "$coproc" --wifi-sta "$ap" --debug wifi-frames &
softap=$!
status=0
for pid in "$sta" "$scan" "$sntp" "$softap"; do
    wait "$pid" || status=1
done
exit "$status"
