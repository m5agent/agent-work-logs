# LX6-B factory firmware and library follow-up

Both original factory images now exercise the classic hardware buses through their application screens. The replay ran 85 compiled Arduino cases. 83 passed and two reproduced pinned library defects. Seven source cases still fail to compile. Both factory images and both device-local controller probes passed their declared functional checks.

The prior failures remain recorded at `f528744221077c59a7ba6a5eeb146ec7bda90ff5`. The results below were captured from a clean checkout at `63f25e3147f84379d3fdd2dd076f3128d5b34d14` using native binary SHA-256 `92dbedd60ed493c439b4482908db7fea22c228d3e985b8f8ab523145fbb7d85a` and classic ROM SHA-256 `920b70635440517866aab2230964a570d2cf2b676658d93c52fbac108c1cca31`. [Previous qualification](https://github.com/m5agent/agent-work-logs/tree/a165414a20db7abb9b9eaa54f6ebe793a2d4e82f/records/esp32sim/2026-11-27-lx6b-stick) [Source commit](https://github.com/m5agent/esp32sim/commit/63f25e3147f84379d3fdd2dd076f3128d5b34d14)

## Four findings

- **StickC temperature — LIBRARY-DEFECT.** M5StickC 0.3.0 `MPU6886.cpp:208–212` starts a burst at `0x41` and decodes offsets 6–7. InvenSense DS-000193 rev 1.1 §§7, 8.30 and 8.33 map temperature to `0x41–0x42` and gyro Z to `0x47–0x48`. An independent exact-board UART guest read pairs `0000/0000`, `f99e/0000`, `0cc4/0000` and `0cc4/0800` through I²C. The original example's frame only changed in the gyro-Z trial. [Pinned library](https://github.com/m5stack/M5StickC/blob/202fddddf05d878381f3b4d5bfa6b6e70031a290/src/utility/MPU6886.cpp#L208-L212) [InvenSense register map](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/datasheet/core/MPU-6886-000193%2Bv1.1_GHIC_en.pdf)
- **StickC Plus buzzer — LIBRARY-DEFECT.** M5StickCPlus 0.1.1 `Speaker.cpp:14,31,55` attaches GPIO2 with zero frequency and calls the pin-based tone API with channel constant 0 from `Config.h:12–13`. M5Stack Arduino core 3.2.5 `esp32-hal-ledc.c:186–194` rejects the attach before binding the pin. Lines 409–439 configure a timer for a pin with an existing LEDC binding. The stock example's ELF trace saw attach on GPIO2 at 0 Hz and tone on GPIO0 at 4000 Hz, with zero timer configurations. The separate GPIO2 control produced 3993.610 Hz at 50% duty. Core archive SHA-256 `359821796882142bc4a74e9f16bf2042ab825df47949407d9a600ad5996cca19`. [Pinned library](https://github.com/m5stack/M5StickC-Plus/blob/90cb1bc192d5a4fb6d801191da56e84e0b2f85ad/src/utility/Speaker.cpp) [Exact Board Manager core archive](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/arduino/m5stack-3.2.5.zip)
- **M5Stick factory — PASS.** The original firmware's ESP32 I²C0 transfer now writes `0x75` to MPU9250 address `0x68` and reads `0x71`. The 64×128 SH1107 glass maps its first visible common to the factory's `D3 0x60` setup. The G35 input at 3.0 s drew the factory text while held and returned to black after release. GPIO17, GPIO19 and GPIO26 were active in the factory capture. [Factory source](https://github.com/m5stack/M5Stack/blob/40c3d80dec19b291600de6decd3a0b65340a729d/examples/Stick/FactoryTest/FactoryTest.ino#L18-L75) [SH1107 datasheet](https://files.waveshare.com/upload/1/16/SH1107V2.3.pdf)
- **StickT2 factory thermal UI — PASS.** The Lepton 3.0 CCI `Wire1.endTransmission()` returned address NACK (`2`) during the setup writes to `0x2a`. The baseline ESP32 controller executed the first command with an empty transmit FIFO and sent `0x00`. After the fix, CCI wrote the OEM VSYNC mode and delay (`0x4855`, `0x4859`), then the original firmware received the camera stream on HSPI and rendered independent input scenes. The trace observed 64 complete VoSPI frames for each 8.5 s capture, with no `error=` UART messages. BtnA changed RGB to GRAY. The original app also read an injected encoder delta of +5, cleared it at register `0x20` and changed the temperature-range frame. [Factory CCI source](https://github.com/m5stack/M5-StickT/blob/a502cb40e0837bccd55a3e09389f3cbfc155cea8/examples/M5StickT_Lepton_opensource_v1/lepton.cpp#L349-L365) [StickT2 controls](https://docs.m5stack.com/en/core/StickT2) [FLIR VoSPI integration](https://oem.flir.com/learn/thermal-integration-made-easy/spi-and-i2c-with-lepton/)

## Implementation and reproduction

M5Stack recommends its 1.0.8 board package for the StickT2 source. Its HAL matches the legacy ISR driver and its Wire code maps both address and data ACK failures to return code 2. The baseline bus trace identifies the address stage for this failure. [Exact legacy board package](https://static-cdn.m5stack.com/resource/arduino/m5stack-1.0.8.zip)

Classic ESP32 supports transaction-start and FIFO-watermark interrupts and clocks interrupt-filled transfers from the APB scheduler. An empty FIFO pauses the command until the driver supplies data or the APB timeout expires. Prefilled command lists complete synchronously. M5Stick reuses the existing MPU9250, AK8963, IP5306 and SH1107 models. StickT2 reuses the existing FLIR Lepton and encoder. [ESP32 register definitions](https://github.com/espressif/esp-idf/blob/v5.5.4/components/soc/esp32/register/soc/i2c_reg.h) [Legacy Arduino interrupt driver](https://github.com/espressif/arduino-esp32/blob/1.0.4/cores/esp32/esp32-hal-i2c.c)

```sh
CARGO_PROFILE_RELEASE_LTO=false CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16 \
  cargo build --locked --release -p esp32sim --bin esp32sim
python3 tools/run-lx6-stick.py "$BOARD" target/release/esp32sim "$PLAN" \
  "$CATALOG_IMAGE" "$CLASSIC_ROM" "$OUT" --probe-stock "$ATOM_LITE_IMAGE"
cargo test --locked --release --workspace --no-fail-fast -- --include-ignored --skip external_ --test-threads 5
cargo clippy --locked --workspace --all-targets -- -D warnings
cargo clippy --locked --release --target wasm32-unknown-unknown -p esp32sim-wasm --features jit-tests -- -D warnings
```

Run the runner for each of the six board codes listed below. Use the product docs and catalog input revisions in the preceding qualification. The evidence files give the exact firmware and script digests, emulator exit, UART and framebuffer hashes. The native runs terminate on their emulated-time bounds.

## Matrix totals

| Board | Arduino PASS | LIBRARY-DEFECT | DOCS-DEFECT | Stock or factory | Device-local probe |
| --- | ---: | ---: | ---: | --- | --- |
| StickC | 37 | 1 | 6 | PASS | — |
| StickC Plus | 28 | 1 | 0 | PASS | — |
| StickC Plus SE | 8 | 0 | 0 | PASS | — |
| StickC Plus2 | 10 | 0 | 1 | PASS | — |
| M5Stick | — | — | — | PASS | PASS |
| StickT2 | — | — | — | PASS | PASS |

### StickC (`stickc`)

| Case | Status | Observation | Firmware SHA-256 |
| --- | --- | --- | --- |
| `axp192_m5stickc-1` | PASS | Two simulated battery levels changed the documented display versus default. RGB CRC32 `0473f209` | `62abe7c1a4643b924bf6469fcaaf98a01a0063561416b79d60b4d7e0e4fa66a4` |
| `axp192_m5stickc-2` | PASS | M5.begin addressed AXP192 and enabled the panel rails and backlight. RGB CRC32 `58a2b0f8` | `3c0437148504055ffe11bbffddfa7d1104d747027d3ebbac7e3dc9b1425d66f4` |
| `axp192_m5stickc-3` | PASS | AXP192 shutdown removed panel power after an active frame. RGB CRC32 `58a2b0f8` | `e8551a16821bac25ca7f86312cab9a7917f4e9cfd95e0894c1c8396f9860a058` |
| `axp192_m5stickc-4` | PASS | AXP192 LDO2 brightness followed the guest ramp. RGB CRC32 `5ca7b52c` | `95a633e17fc1d78cd3284d3f342062501d5b964a8c3fedf4ac3df7482617eab6` |
| `axp192_m5stickc-5` | PASS | Guest ScreenSwitch changed the visible backlight across the two checkpoints. RGB CRC32 `58a2b0f8` | `95fd553ae2bc19f2d55174d95d0778a2eff92f769e643c53390bb6030ff304fb` |
| `button-1` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `c961d988` | `c150f847948b2c253c3933b0bf181bf0d44b44ed98c0fe3fd65edd983b0284f5` |
| `button-2` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `f4ea7e17` | `5f02d5723562aba40e5e2de46297ecaff0a7b51861f3e0d89fc34095b7cc07c0` |
| `button-3` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `9630157a` | `002cc4d1c785f570cf3b256818de6e07c0e3cdcae55b6f50b7c01783b448ce6a` |
| `button-4` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `6b043693` | `b3da4f24e4a78d5f5f9a37cb54277a4e2be9b2ad86585e4438c472c4e15f684a` |
| `button-5` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `13badb7e` | `56378790154b34df9e9ab2f90198f7d1057d2722c6ece60ed09c3e0639c336dd` |
| `button-6` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `9feb0946` | `87df458ce478e8f7794a05a6bce715579abee719d955cbc3367199c3fe8085aa` |
| `button-7` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `49ded953` | `57a7a079c5e35d8b11be49766a4c1a00b9791c57dab063aea1b931586c723681` |
| `button-8` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `4eaae4ec` | `919935a93ea4820d9f6972c408eb293c83ad9d6698212db5423ceaf7faa590ef` |
| `button-9` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `51f0834b` | `b3d5e9f56cdc29d6c95e72b537b583ffbf0ca5ed743bd3d8a4bc1f49760b6541` |
| `imu-1` | PASS | Legacy sensor initialization returned success on UART. RGB CRC32 `58a2b0f8` | `0b7c507d8ff9106bd55d5a75587031367af714ded24f71c715c6788d9a7bc05d` |
| `imu-2` | PASS | Distinct injected sensor inputs changed the application display versus idle. RGB CRC32 `d4ea0cd6` | `3f6b09d6f83ad5e3f82e03487d70a6f3d790e1ca0f760a4a7d773f664043d26f` |
| `imu-3` | PASS | Distinct injected sensor inputs changed the application display versus idle. RGB CRC32 `2c1d427f` | `7b3c5a1b585ee22264c9980bdb20cebf274d8fdfeba9e640e9d31db3371c6dd2` |
| `imu-4` | PASS | Distinct injected sensor inputs changed the application display versus idle. RGB CRC32 `3e911e5b` | `8e4b1e1c3c497e8f3661cf5a7280d5c3ffba1f952794ef5ee385fda90a127505` |
| `imu-5` | LIBRARY-DEFECT | Temperature-only inputs preserve the frame and gyro-Z changes it. The library decodes 0x47–0x48. `M5StickC 0.3.0 src/utility/MPU6886.cpp:208–212`. RGB CRC32 `7bf5d411` | `e9eb9003eeb49d9ef67d799d6244fec0d7afe4ced0f4e5f0e59543e7e160c5ee` |
| `lcd_m5stickc-1` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `6c648fe0` | `9a521939aeeb4b88c89585fa1038dc72568e4e702b46b0eeccec8f02773e351d` |
| `lcd_m5stickc-2` | PASS | The 22-character red-on-white text matches its glyph counts and wrap. RGB CRC32 `5e896154` | `fca5e0baa17c64644baddfe5a3275cb3d979a3d64719dfc73c2d4c693b55e9c0` |
| `lcd_m5stickc-3` | PASS | Default-font glyph counts and the documented cursor placement match. RGB CRC32 `1c84091c` | `04a17a8f44ccfb06654fbb96723c165af1f2730e811d8e720e76c35aa7bcbd69` |
| `lcd_m5stickc-4` | PASS | Default-font glyph counts and the documented cursor placement match. RGB CRC32 `a053d439` | `64d958579d303770542ba6ebd363abe7332c8a967caf213c90b47799b507dfa4` |
| `lcd_m5stickc-5` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `0dfd548f` | `5063c3addace44f63a3719ac50b909630241cec5f8acf2e61788afa10176b115` |
| `lcd_m5stickc-6` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `ca5f451b` | `2e20e12f29b6718acd4f70e4f90e426302807ff8f8f278b20b1a910ce247515d` |
| `lcd_m5stickc-7` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `d213684d` | `dfa74ce39612c81ab04a79c29f99f1cdacd9274f1e3a165c629341186a8d1e90` |
| `lcd_m5stickc-8` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `25a65894` | `ac3c3d8cf7d8ea3ed96a769a2653f55b1b8716db0acd02f938cf8571faf8532f` |
| `lcd_m5stickc-9` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `deb47030` | `15f0391f2b261f67e739588851ced896105b030251d73cfcb9d23128302b5337` |
| `lcd_m5stickc-10` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `6ed67251` | `1366a2472d5c1313fb2a601228d187ed0e17d8c8a61830126daeaf4582ff695b` |
| `lcd_m5stickc-11` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `4e645375` | `14bb2207f75e8deb927ca34d02e43e1585e7b31cb8d9aba411bd85aabca7feb0` |
| `mic` | PASS | Both PCM tones changed the guest waveform relative to silence. RGB CRC32 `95f5dd26` | `48b815dbca7c3b5cc40560724d9d4a520e5cc32fc38946ce69204dbd1e0357ac` |
| `pwm-1` | DOCS-DEFECT | LEDC 2.x functions removed by the pinned Arduino-ESP32 3.x package. `static/en/arduino/m5stickc/pwm.md:31,35` | — |
| `pwm-2` | DOCS-DEFECT | LEDC 2.x functions removed by the pinned Arduino-ESP32 3.x package. `static/en/arduino/m5stickc/pwm.md:63–64` | — |
| `rtc-1` | PASS | Guest RTC write changed the BCD calendar and virtual time advanced. RGB CRC32 `58a2b0f8` | `ded3fde9e6bc00adf618e358462f0389088d2892b7e75a588a81454871ca7929` |
| `rtc-2` | PASS | Guest RTC write changed the BCD calendar and virtual time advanced. RGB CRC32 `f8b4c625` | `bd136ff9ef068e4a4b8aa28127ee59ee7ba4cf37218f68e9cb4fc02ef19108f0` |
| `rtc-3` | PASS | Guest RTC write changed the BCD calendar and virtual time advanced. RGB CRC32 `58a2b0f8` | `1c99d741b562331b96791dc26de0040331d91275440a36e7adb3aac8b07533e3` |
| `rtc-4` | PASS | Guest RTC write changed the BCD calendar and virtual time advanced. RGB CRC32 `d938eb90` | `0550554cb2b60c693c4db55c44532673911f9a354ac00130182c3b8f70a65a5a` |
| `sh200q_m5stickc-1` | DOCS-DEFECT | M5StickC 0.3.0 IMU does not expose I2C_Read_NBytes. `static/en/arduino/m5stickc/sh200q_m5stickc.md:23` | — |
| `sh200q_m5stickc-2` | DOCS-DEFECT | getGyroData accepts float pointers, example passes int16_t pointers. `static/en/arduino/m5stickc/sh200q_m5stickc.md:37,50` | — |
| `sh200q_m5stickc-3` | DOCS-DEFECT | getAccelData accepts float pointers, example passes int16_t pointers. `static/en/arduino/m5stickc/sh200q_m5stickc.md:68,81` | — |
| `spm1423_m5stickc` | PASS | Both PCM tones changed the guest waveform relative to silence. RGB CRC32 `9ff79229` | `48b815dbca7c3b5cc40560724d9d4a520e5cc32fc38946ce69204dbd1e0357ac` |
| `system_m5stickc-1` | DOCS-DEFECT | standalone sketch omits Arduino loop(). `static/en/arduino/m5stickc/system_m5stickc.md:51–56` | — |
| `system_m5stickc-2` | PASS | System function displayed the BM8563 clock and its time advanced. RGB CRC32 `6e6b2e2e` | `1c53bcb79b7b0875669fa0aee1f8ab6e35cb42e3ff1933feb57600b08dc325f2` |
| `quickstart-helloworld` | PASS | The Hello World glyphs occupy the expected region seen in the product photograph. RGB CRC32 `afb49adb` | `9f0e042130f8a3f37767395185b83fdb159c97a0e587f0b6aa701cfa3ad0f944` |
| `stock` | PASS | Stock menu changed after input. UART REPL read both buttons. RGB CRC32 `bcada87c` | `2463fc362f6acfacccb678a2c40aeb733e470ca793ec4a100d2e077baa641f03` |

### StickC Plus (`stickc-plus`)

| Case | Status | Observation | Firmware SHA-256 |
| --- | --- | --- | --- |
| `button-1` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `4f211740` | `888dea34801a605063e9e99732f5a0127a1bca87ee70f5994c62acadf7c1fc4f` |
| `button-2` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `796106b8` | `e99974a1cd92896c0f27a1c72cfb0bc860aecd4f5e61728b5f5e215259fd6a76` |
| `button-3` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `d0c50962` | `2ff6cf327405c27e3e7fef9fee0949b0e78d295e3065708b19bd4b62cafa174d` |
| `button-4` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `2141bf94` | `83b15ce95278ec5f46e4846c84e30078274b53f0075150febc0ee2e82d9fb19c` |
| `button-5` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `0cd7d759` | `a7250b1e2b22a2359cc43cd643c7616dc17a05e8ce5f8326848a483a68c0880c` |
| `button-6` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `cdb8bae1` | `96ae6add94683a15af10045e550e4566e24c1036d1776a51af2a9eee973c6d2f` |
| `button-7` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `29730ce2` | `5ab4a468a4cdacdaee57c5951f8b965ddb8bb80bfec743dc75e5554100166666` |
| `button-8` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `8d3a1048` | `192fcc2669ce61464e6e981e17997a2550d10725e8a7fd5d4ca68f1047757390` |
| `button-9` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `eec56209` | `34d7fa4920d7cc28e66a089376c01933980691c04a0c9e13e0426d25c0c65467` |
| `buzzer` | LIBRARY-DEFECT | GPIO2 attach requested 0 Hz, tone addressed GPIO0, and no LEDC timer was configured. `M5StickCPlus 0.1.1 src/utility/Speaker.cpp:14,31,55`. RGB CRC32 `fae23ff0` | `892df1588bc1e7b9b2830ecdd728ae5f33f794dc3e2728d74954d2e206be7d4b` |
| `display-1` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `169842c2` | `d12af2354876377a3047282ce27680d58095415fcac73e0156762b47212b04c8` |
| `display-2` | PASS | The 22-character red-on-white text matches its glyph counts and wrap. RGB CRC32 `9d60731d` | `9fc8f3567f62a2dbc4a2de298e91b121535df89d4cea8b3a52350bba09126b0a` |
| `display-3` | PASS | Default-font glyph counts and the documented cursor placement match. RGB CRC32 `c9885213` | `fd8837bac9ab53bce5d5fb5f7ed853075e60ade4c9743c58161c9df65985c47b` |
| `display-4` | PASS | Default-font glyph counts and the documented cursor placement match. RGB CRC32 `e489d84c` | `d45c1e56b89df6084ca9fc43af45dfc4c108fa9303a88512fd42daad6eee23ce` |
| `display-5` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `11593d20` | `282561b7681766c8f0c71eb9b40ba0fb04fb1186c78215704f43736888024e5e` |
| `display-6` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `3687985a` | `968032a976a6ab34d1fe84fbc725b4a13d139599a5c911f5c4bc71a28f7daf68` |
| `display-7` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `300bf109` | `849e744121255d6a9f7856c40986f56b39482797c5300f21469758692ba4375a` |
| `display-8` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `c4f9ae31` | `f1ba0b496701350b9a4426070bff4e8a96bfde573eca0e95ab02ed44afd7894a` |
| `display-9` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `70d7ddb6` | `c219690b582a16cf551e2ec801452c65cfbf4bc3ec3fde1295578d204a287cf9` |
| `display-10` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `d20f951a` | `b8a766a3b6cc6fa57c164debf92ca145c61f772b8515c9845c6872c14657b000` |
| `display-11` | PASS | Visible pixel count or fill color matches the sketch operation. RGB CRC32 `437846bc` | `a3118e2fa919326ae07f005d488e80a08116da235eb6d3f91a2799e6e0b17038` |
| `imu` | PASS | Distinct injected sensor inputs changed the application display versus idle. RGB CRC32 `3f6d14d5` | `7cd2b87fee0ef84064440dae694cf2a0fa7af0817059e90a1dba67cff7e07c0c` |
| `mic` | PASS | Both PCM tones changed the guest waveform relative to silence. RGB CRC32 `8f3e80db` | `cafb6ee55228503e6fcdb176de0dcb4630d3bc92531babe45099611f430604af` |
| `power-1` | PASS | Two simulated battery levels changed the documented display versus default. RGB CRC32 `7e9510a7` | `64c8255d142167fced09df1d287f26f7744924e1e3dc225bcbaf47ddb0bc1cbd` |
| `power-2` | PASS | M5.begin addressed AXP192 and enabled the panel rails and backlight. RGB CRC32 `fae23ff0` | `091c5aafad0a5c4da5fd8e1f632dfebbc2b1370b013da3beb49ea96947a9c159` |
| `power-3` | PASS | AXP192 shutdown removed panel power after an active frame. RGB CRC32 `fae23ff0` | `e739748b9774bc75318f3b727aba0ce1b057aca5617d8e979b4f63bb6dec5324` |
| `power-4` | PASS | AXP192 LDO2 brightness followed the guest ramp. RGB CRC32 `2fed8d55` | `51b933338c0a917750102653ffd571fdc8c1d2b7f08fcf766c943a8fcaa1b8c6` |
| `power-5` | PASS | Guest ScreenSwitch changed the visible backlight across the two checkpoints. RGB CRC32 `fae23ff0` | `0a87807d9c41e40d93cdef25205fed3ad1f7c515a4656a2ffc86476e84e78ad2` |
| `quickstart-display` | PASS | The color-fill sequence advances to the documented Display Test lettering. RGB CRC32 `1d67dcb5` | `7c66d997cd0976b3a0f24e3ca84dc815bc8e3c2f40a1fa6cc7ac0d0d70aa558c` |
| `stock` | PASS | Stock menu changed after input. UART REPL read both buttons. RGB CRC32 `6f764c14` | `6e82447cc87695703dc973a3d2bac00e34619bd5d011970df19f548923241cb2` |

### StickC Plus SE (`stickc-plus-se`)

| Case | Status | Observation | Firmware SHA-256 |
| --- | --- | --- | --- |
| `battery` | PASS | Two simulated battery levels changed the documented display versus default. RGB CRC32 `c9dd8e4a` | `76c34229b01a81e4401b7f3251e98cc86e818e375fdab8d2aced53660e5e1849` |
| `button` | PASS | Scripted GPIO input changed the documented button display versus idle. RGB CRC32 `2fede38f` | `4241d8be2461d6444c60d5cca6263417a303af6e9d0bda63ec26ce132b0b8612` |
| `display` | PASS | Native frame shows the expected 20×20 rectangles and circles at distinct checkpoints. RGB CRC32 `b74986ae` | `ec4b2bae22a0bc8516d9deba500b09a171d8e17c4a9a31df5841234ef3b1d730` |
| `ir_nec` | PASS | Decoded two expected NEC commands from the active-low GPIO9 PWM envelope. RGB CRC32 `3d8c5a5a` | `d73af24be9df6bde3c56db6fb1b3dc6081ee8aa092756dbcf939d2f632dcf65d` |
| `mic` | PASS | Distinct tone and silence frames. routed replay bursts (Hz, ms) [(738.1, 989.0)]. RGB CRC32 `a5a45e24` | `8e85f5f98100e55722fc419d760b3e76fac85127a12f78be3790990cb1319e1b` |
| `speaker` | PASS | Routed I2S piezo bursts (Hz, ms) [(7000.2, 99.9), (4000.0, 199.8), (7000.2, 95.9), (4000.0, 199.8), (6999.8, 97.1), (4000.0, 128.0)]. RGB CRC32 `f9ca3772` | `3e16d4b062dd0103e0d43442e5706c61b3c9885719ccd5f065cc3726ef414f8a` |
| `wakeup` | PASS | Timed wake reset followed scripted button input and idle showed one boot. RGB CRC32 `182770fd` | `921ada10019f9e4c9990352d5edd0a94f191e77be3460cb8616c605e293fe0a8` |
| `quickstart-scrollgraph` | PASS | Six plotted colors and grid span the native display and advance across checkpoints. RGB CRC32 `b5e3572c` | `9b7bebf1eed5f422f22e513825da33c5b9ac8ca66ddc570bd8b06b078736e29a` |
| `stock` | PASS | Stock menu changed after input. UART REPL read both buttons. RGB CRC32 `685e6dab` | `0c7055bb8e64afe1d8fa4fd4bdc0961ca0d6366351aca5d6c83eaaf72155ee88` |

### StickC Plus2 (`stickc-plus2`)

| Case | Status | Observation | Firmware SHA-256 |
| --- | --- | --- | --- |
| `battery` | PASS | Two simulated battery levels changed the documented display versus default. RGB CRC32 `4ed97b18` | `a9fcbe8608c541b9de39399e6d535c0e097752201e041cacc1f87ae9b0a7a09a` |
| `button` | DOCS-DEFECT | M5StickCPlus2 1.0.1 exposes BtnC, example calls BtnPWR. `static/en/arduino/m5stickc_plus2/button.md:33,36` | — |
| `buzzer` | PASS | Routed I2S piezo bursts (Hz, ms) [(10000.4, 99.9), (4000.0, 19.8), (10000.4, 99.9), (4000.0, 16.2), (10000.4, 99.9), (4013.6, 18.4)]. RGB CRC32 `f5f70cd7` | `5582c83519a02dd7af8034b966065256cf90244129437c09bf0bd82cee66e6de` |
| `display` | PASS | Native frame shows the expected 20×20 rectangles and circles at distinct checkpoints. RGB CRC32 `dfa326ea` | `499ff2c14be1e2cc6424f4855bcec2ce01de37dca2c9b08efd796611b5b4fb4f` |
| `imu` | PASS | UART reports both injected accelerometer vectors and the idle control ran. RGB CRC32 `ab003362` | `abfb648a8e8493df181e049ce8d8f547bd1b211d29c0740fd4df329924778ddf` |
| `ir_nec` | PASS | Decoded GPIO19 NEC codes cb341111, ca351111, c9361111, c8371111, c7381111. RGB CRC32 `bc0056a8` | `c5648898ff9354b5c618d7bcb7b2f8454a786af134177ce985a04ed834cec055` |
| `led` | PASS | G19 SET/CLR edges observed through the GPIO controller. RGB CRC32 `4f757d51` | `bc93ea3cf0931072c3d03a296cabc8a51c398be21296e0ac5285396392f40e34` |
| `mic` | PASS | Distinct tone and silence frames. routed replay bursts (Hz, ms) [(732.9, 1049.2)]. RGB CRC32 `df8a0fab` | `fb7b241abbb1168d8f97286b4f5ab1ad0c37a7efb9c9205f18e443547d095791` |
| `rtc` | PASS | Virtual Wi-Fi/SNTP populated the hardware RTC. RGB CRC32 `92790915` | `b7c2850ec9a3d3be1a46722261207e46ceba6976991e9cc78f56eaa1b25ea055` |
| `wakeup` | PASS | Timed wake reset followed scripted button input and idle showed one boot. RGB CRC32 `990cf002` | `83c12e633a21f5bf55a2dc8ae8933d1103312e4fa00dca190116544154d693a3` |
| `quickstart-display` | PASS | Native frame shows the expected 20×20 rectangles and circles at distinct checkpoints. RGB CRC32 `dfa326ea` | `b660a3cf47a64ed3e5506e164f4ca8f1b431c3f77c79693b1c9e5a074b3fba35` |
| `stock` | PASS | Stock menu changed after input. UART REPL read both buttons. RGB CRC32 `7f594e68` | `712fd8ca7d232ca84b1214610b7b7933bca4f19233258736d0db33147b4342dc` |

### M5Stick (`m5stick`)

| Case | Status | Observation | Firmware SHA-256 |
| --- | --- | --- | --- |
| `factory` | PASS | Original firmware read WHO_AM_I 0x71, drew the test text while G35 was held, cleared it after release and drove G17/G19/G26. RGB CRC32 `9de2a48d` | `84228dfb6f0dd9b84b63c33f93a53545d8d43658893f432e3eaf4313923bffca` |
| `probe` | PASS | Controller probes check sensor input readback and native framebuffer. RGB CRC32 `e668d4ee` | `8d13d287e18c56a8a27e5bf1617dca81a1c6d847dc302f034f09854753c184d0` |

### StickT2 (`stickt2`)

| Case | Status | Observation | Firmware SHA-256 |
| --- | --- | --- | --- |
| `factory` | PASS | Original firmware completed CCI and VoSPI, showed two thermal scenes and switched palette after BtnA. RGB CRC32 `edbdabe6` | `bb33ffd41f9c6f9235b2fb44eac893b7ce6f70879f48eed9cb1ff75ef9419cd7` |
| `probe` | PASS | Controller probes check sensor input readback and native framebuffer. RGB CRC32 `f63c63b5` | `8d13d287e18c56a8a27e5bf1617dca81a1c6d847dc302f034f09854753c184d0` |

## Shared regressions and limits

- CoreS3 15/15 and Cardputer-ADV 11/11. Classic and S3 UART sentinel output was byte-identical to the earlier baseline. The per-core instruction counts remained 4,342,917 + 431,305 and 2,658,432 + 1,084,186.
- The LX6-A Atom regression replay matched the preceding status map. AtomU stock and Atom Echo stock retain their previous failures. The original ESP-IDF receiver fixture also passed on all five StickC-family profiles using two NEC packets, an idle control and raw PDM readback.
- Workspace tests reported 1997 passing and 7 failures already present at the preceding head. The failures are `hello_world_p4_rev3_smp`, `hello_world_p4_smp`, `hosted_p4`, `hosted_p4_rev3`, `hosted_rawtp_rx`, `hosted_rawtp_tx`, `wifi_sta_is_refused_where_it_does_not_work_yet`. Native and WASM Clippy passed. [Regression evidence](evidence/regression-summary.json)
- StickT2 virtual images use synthetic Raw14 values. Numerical temperature readout remains partial because the original guest divides the value in CCI register `0x0006` by two before requesting GET data. The device-local probe reads the modeled single-word payload, `0x75a3`, directly. FLIR specifies host-written lengths in 16-bit words. The original guest displayed −212.22 for the synthetic high sample while its FPA value remained zero. Physical GET length readback was not run because the hardware discovery request timed out. [Factory GET code](https://github.com/m5stack/M5-StickT/blob/a502cb40e0837bccd55a3e09389f3cbfc155cea8/examples/M5StickT_Lepton_opensource_v1/lepton.cpp#L382-L395) [FLIR IDD §2.1.6 and Fig. 2](https://groupgets-files.s3.amazonaws.com/purethermal/Lepton-Software-IDD-Rev303.pdf)
- Physical hardware, acoustic output, IR optics, heat calibration and browser runtime are outside this execution. The host outputs are virtual controller evidence. The prior result remains independently archived. Reverting the follow-up commits restores the previous batch behavior.
