#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
coproc=c6:bootloader=firmware/c6-bootloader.bin,ptable=firmware/c6-partitions.bin,otadata=firmware/c6-otadata.bin,app=firmware/c6-app.bin
ap=$(python3 - <<'PY'
from pathlib import Path
import re
s = Path("firmware/wifi-1/sketch/sketch.ino").read_text()
ssid, password = [re.search(r'\b' + name + r'\s*=\s*"([^"]*)"', s)[1] for name in ("ssid","password")]
assert (ssid, password) == ("ssid", "password"), "expected the published example's placeholder AP values"
print(f"ssid={ssid},psk={password}")
PY
)
for pair in wifi:wifi-1 scan:wifi-2 sntp:rtc-2; do
    name=${pair%:*}
    sketch=${pair#*:}
    ./run_tab5.sh m5stack-tab5 "tab5-$name-ap" "firmware/$sketch/sketch.ino.merged.bin" 12 --coproc "$coproc" \
      --wifi "$ap" --net virtual,epoch=1764150000 --debug wifi,net &
done
wait
