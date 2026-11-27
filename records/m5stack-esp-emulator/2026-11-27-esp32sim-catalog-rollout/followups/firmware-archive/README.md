# Cardputer K132 firmware archive

The display, keyboard and microSD examples were rebuilt under two different
build directories with the same pinned toolchain and path mapping. All 15
build files matched across directories and the path scan found no private
paths or identity strings. Each exact merged image passed its native
Device Service guest check with the radio-sync runtime.

The fresh archive clone verified 279 public files, 29 indexed Arduino
case manifests and LFS object integrity. The three new entries are
Cardputer K132 Arduino cases. Stock images remain fetch-only. The remaining
319 new prebuilt examples have no published path-clean rebuild in this batch.

[Published archive and per-case docs index](https://github.com/m5agent/m5stack-firmware-archive/tree/e7529229fe8b2e8e76aecfcdbe5a37c0c21619b3/devices/cardputer/arduino-docs)
· [Rebuild recipe](https://github.com/m5agent/m5stack-firmware-archive/blob/e7529229fe8b2e8e76aecfcdbe5a37c0c21619b3/build-records/rebuild-2026-11-27-cardputer.md)
· [Readback receipt](summary.json)
