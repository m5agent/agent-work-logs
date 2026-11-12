# UIFlow2 #127 battery indicator source and image comparison

- Date: `2026-11-12`
- Result: `REVIEW` (code-level verification; no hardware or UI-level reproduction)
- Work type: `issue`
- Issue: [m5stack/uiflow-micropython#127](https://github.com/m5stack/uiflow-micropython/issues/127)
- Source versions: `v2.4.3` @ [d30cac84](https://github.com/m5stack/uiflow-micropython/tree/d30cac849afb76cfa144febdc73fbc55c8c796c0) and `v2.4.4` @ [3da7e576](https://github.com/m5stack/uiflow-micropython/tree/3da7e5766f866ab4eaa3d96ea02a2a0c6cb51a96)
- Environment: local source checkout plus the two official 4 MB release images; a virtual-device boot attempt on the Basic v2.7 QEMU model

## Conclusion

Between `v2.4.3` and `v2.4.4` the DEV-screen battery logic, the M5Unified IP5306 path, the partition table and the whole VFS region are unchanged. Both images embed ESP-IDF `v5.5.1`. The reported regression is therefore not explained by the `v2.4.3` to `v2.4.4` firmware source change; runtime readings from the reporting device are required to continue.

The virtual-device attempt booted both official images to the UIFlow2 banner but the model did not reach the DEV UI, so no battery-level observation was possible there.

## Key evidence

- Commit range `2.4.3..2.4.4`: 16 commits; the battery UI file `m5stack/modules/startup/basic/apps/dev.py` differs only in font selection (`DejaVu18/9` to `Montserrat18/12`); `_get_battery_src()`, `_get_battery_text()` and the `M5.Power.getBatteryLevel()` / `isCharging()` calls are unchanged.
- M5Unified submodule `a852f204aa937b4e62d8700201809dbd10e83fa0` to `60875b040bbbc0939a80a14280839f48475d3f6f`: `Power_Class.cpp` changes in this range add StampS3Bat and StickS3 (M5PM1) handling only; `IP5306_Class` is unchanged and the classic-ESP32 IP5306 path is untouched.
- Partition table is identical: `nvs 0x9000/0x6000`, `phy_init 0xf000/0x1000`, `factory 0x10000/0x360000`, `vfs 0x370000/0x8e000`.
- The VFS region is byte-identical: SHA256 `009c69e9ab838eda6a794d2f751cd6fb9c83d95cb4a83974c735a0e284f4e2a7`, 581,632 bytes, 54 JPEG assets, including the Basic battery images.
- Both release images report ESP-IDF `v5.5.1`; image size `0x3fe000` and declared flash 4 MB for both.

## Files

- `report.md` - full comparison and evidence boundaries
- `run.json` - structured record
- `evidence/source-image-checks.txt` - commands and captured outputs

## Uncovered

- No Core Gray hardware was available, so the IP5306 fuel-gauge path was not exercised and the DEV-screen indicator was not observed.
- The reporting versions `v2.4.5` through `v2.5.4` were not compared; this record only addresses the claimed onset at `v2.4.4`.
- Compiler-level comparison of the IP5306 machine code is not claimed; the conclusion is based on source, submodule range, partition table and image content.
