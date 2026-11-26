#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"
printf '%s\n' '2.0 contact 0 160 400 1' '2.1 contact 1 540 880 1' > gt-multi.txt
printf '%s\n' '2.0 imu 0.5 -0.25 1.0 125 -50 25' > imu.txt
printf '%s\n' '2.0 battery 7980 410 1' > battery.txt
printf '%s\n' '3.0 touch 360 640 1' '3.25 touch 360 640 0' > wake.txt
run() {
    local name="$1" sketch="$2" seconds="$3"
    shift 3
    ./run_tab5.sh m5stack-tab5 "$name" "firmware/$sketch/sketch.ino.merged.bin" "$seconds" "$@"
}
run tab5-multi touch-2 3.1 --script gt-multi.txt --debug i2c1 &
run tab5-imu imu-1 4 --script imu.txt --debug i2c1 &
run tab5-power power-1 4 --script battery.txt --debug i2c1 &
run tab5-rtc rtc-1 5 --debug i2c1 &
wait
if [[ -s tab5-sd-seed.img ]]; then
    cp tab5-sd-seed.img tab5-sd-run.img
    run tab5-sd microsd-1 6 --sd-rw tab5-sd-run.img --debug spi2
    ./run_tab5.sh m5stack-tab5 tab5-sdmmc sdmmc-probe/build/sketch.ino.merged.bin 5 --sd tab5-sd-run.img --debug sdmmc
fi
if [[ -s tab5-sd-render-seed.img ]]; then
    cp tab5-sd-render-seed.img tab5-sd-render.img
    run tab5-sd-render microsd-1 6.2 --sd-rw tab5-sd-render.img --debug spi2
    cp tab5-sd-render-seed.img tab5-sd-render-second.img
    run tab5-sd-render-second microsd-1 7.2 --sd-rw tab5-sd-render-second.img --debug spi2
fi
./run_tab5.sh m5stack-tab5 tab5-rail-output power-outputs/build/sketch.ino.merged.bin 3 --debug i2c1
run tab5-wake-5s wakeup-1 12 --script wake.txt --debug i2c1 &
run tab5-wake-min-retry wakeup-2 65 --script wake.txt --timeout 420s --debug i2c1 &
run tab5-antenna wifi-3 3 --debug i2c1 &
wait
