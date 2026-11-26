#!/bin/bash
set -eo pipefail
cd "$(dirname "$0")"
cat > press.txt <<'SCRIPT'
2.0 touch 360 640 1
SCRIPT
cat > release.txt <<'SCRIPT'
2.0 touch 360 640 1
2.5 touch 360 640 0
SCRIPT
cat > multi.txt <<'SCRIPT'
2.0 contact 0 160 400 1
2.1 contact 1 540 880 1
SCRIPT
python3 - <<'PY'
from pathlib import Path
steps = [
    (5.6, 'serial import M5; M5.begin(); M5.Display.fillScreen(0x123456); print("TAB5_REPL_DRAW", M5.getBoard())'),
    (6.0, 'touch 233 456 1'),
    (6.2, 'serial M5.update(); print("TAB5_REPL_TOUCH", M5.Touch.getCount(), M5.Touch.getX(), M5.Touch.getY())'),
    (6.5, 'touch 233 456 0'),
    (6.7, 'serial M5.update()'),
    (6.8, 'serial M5.update()'),
    (6.9, 'serial M5.update(); print("TAB5_REPL_UP", M5.Touch.getCount())'),
]
# USB-JTAG REPL consumes CR. NUL keeps CR inside the action's text.
Path("uiflow-repl-cr.txt").write_bytes(b"".join(
    f"{sec} {action}".encode() + (b"\r\0" if action.startswith("serial ") else b"") + b"\n"
    for sec, action in steps))
PY
./run_tab5.sh m5stack-tab5 final-gt-idle firmware/touch-1/sketch.ino.merged.bin 3.1
./run_tab5.sh m5stack-tab5 final-gt-press firmware/touch-1/sketch.ino.merged.bin 2.8 --script press.txt --debug i2c1
./run_tab5.sh m5stack-tab5 final-gt-release firmware/touch-1/sketch.ino.merged.bin 3.1 --script release.txt --debug i2c1
./run_tab5.sh m5stack-tab5-st7123 final-st-multi firmware/touch-2/sketch.ino.merged.bin 2.8 --script multi.txt --debug i2c1
for version in 3 4; do
    ./run_tab5.sh m5stack-tab5 "final-25${version}-release" "firmware/uiflow2-v2.5.${version}.bin" 7.2 \
        --script uiflow-repl-cr.txt --debug dsi,i2c1
done
