# Repeat the validation

Use esp32sim from the source revision in the [manifest](../run.json). Follow the [milestone 2 fixture setup](https://github.com/m5agent/agent-work-logs/tree/b50268351888f4ac0c1f061038188dee6092107a/records/esp32sim/2026-11-26-tab5-launcher/code/board-validation) for the pinned documentation sketches, OCR, stock UIFlow2 images, Maker Fighter, the speaker, probe inputs and writable SD images. The original C6 adapter remains the stock UIFlow2 fixture.

Build the Arduino examples with Arduino CLI 1.3.1, M5Stack Arduino 3.2.5, M5Unified 0.3.0 and M5GFX 0.3.0, FQBN `m5stack:esp32:m5stack_tab5`. Keep the original speaker compiler output at `firmware/speaker-1/compile.log` and its return code in `result.json`. For the standalone AP variant, run `python3 build-softap.py firmware/wifi-1/sketch/sketch.ino wifi-ap/sketch/sketch.ino` and build to `wifi-ap/build`.

Build a separate ESP-Hosted 2.0.13 SDIO slave with [build-c6-wlan.sh](build-c6-wlan.sh) and ESP-IDF v5.4.2. Export `TAB5_C6_WLAN_BUILD` as its absolute build directory. The runner resolves `bb_init` in the C6 ELF. Build timestamps can alter binary digests. The recorded image and ROM hashes identify the tested bytes.

Use `ESP32SIM_ROM_DIR` and `ESP32SIM_P4` for the ROMs and release executable, then run `bash run_all_tab5.sh` in the fixture directory. The SDK USB case uses an explicit full-speed MSC fixture. The existing high-speed register probe remains a separate case.

Apply [the controller ID check patch](register-probe-id.patch) to a copy of the milestone 2 register probe and build to `usb-register-compat/build`. The SDK probe is the original fixture.
