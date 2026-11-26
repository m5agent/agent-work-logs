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

# Stock application validation. The same stock C6 adapter is required for both images.
coproc=c6:bootloader=firmware/c6-bootloader.bin,ptable=firmware/c6-partitions.bin,otadata=firmware/c6-otadata.bin,app=firmware/c6-app.bin
cat > stock-touch.txt <<'SCRIPT'
7.0 touch 83 755 1
7.45 touch 83 755 0
SCRIPT
for version in 3 4; do
    label="stock-final-25${version}"
    image="firmware/uiflow2-v2.5.${version}.bin"
    ./run_tab5.sh m5stack-tab5 "${label}-home" "$image" 9 --debug dma2d,ppa,dsi --coproc "$coproc"
    ./run_tab5.sh m5stack-tab5 "${label}-adc" "$image" 9 --script stock-touch.txt --debug i2c1 --coproc "$coproc"
done

# Prebuilt, separately labeled probe and corrected speaker copies are inputs.
./run_board_tab5.sh
./run_network_tab5.sh
./run_tab5.sh m5stack-tab5 maker-final-prompt68 firmware/maker-fighter-1.4.bin 6.8 --script gamepad-idle.txt --debug usb_otg
./run_tab5.sh m5stack-tab5 maker-final-idle firmware/maker-fighter-1.4.bin 7.5 --script gamepad-idle.txt --debug usb_otg
./run_tab5.sh m5stack-tab5 maker-final-gamepad firmware/maker-fighter-1.4.bin 7.5 --script gamepad.txt --debug usb_otg
printf '2.0 usb-msc fs\n' > msc-full-speed.txt
./run_tab5.sh m5stack-tab5 msc-final-sdk usb-probe/build/sketch.ino.merged.bin 4 --script msc-full-speed.txt --debug usb_otg
./run_tab5.sh m5stack-tab5 msc-final-register usb-register-compat/build/sketch.ino.merged.bin 4.9 --script msc.txt --debug usb_otg
./run_tab5.sh m5stack-tab5 speaker-final-full speaker-1-corrected/build/sketch.ino.merged.bin 12 --wav speaker-1-corrected/final-full.wav --debug i2c1
for source in tone silence; do
    ./run_tab5.sh m5stack-tab5 "mic-final-$source" firmware/mic-1/sketch.ino.merged.bin 4 --mic-wav "mic-$source.wav"
done
./run_tab5.sh m5stack-tab5 mic-final-play firmware/mic-1/sketch.ino.merged.bin 16 --mic-wav mic-tone.wav --wav mic-final-play.wav --script mic-play.txt
python3 check_tab5.py "${TAB5_OCR:-./frame-text}"
