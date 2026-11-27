# LX6-B classic Stick firmware qualification

The six board profiles are available on the LX6-B branch. The Plus SE and Plus2 passed their runnable matrices and catalog startup checks. Two classic Arduino libraries block specific compiled examples. The M5Stick and StickT2 controller probes passed and the two original factory applications remain incomplete.

- Branch head `f528744221077c59a7ba6a5eeb146ec7bda90ff5`
- LX6-A and S3-A base `8e17dcd553fbd59b2dc9034cb5bd8eecb0884302`
- Product docs source `7219cc9286c39b463da84053deee40bc234625db` and catalog source `74ee6cb006105fe8553eb83071e23ae3361a57f1`
- Classic ROM ELF SHA-256 `920b70635440517866aab2230964a570d2cf2b676658d93c52fbac108c1cca31`
- Validation lane native ESP32 virtual device with ROM boot

## Runtime and firmware identity

| Simulator source | Native binary SHA-256 |
| --- | --- |
| `83da911342fbf1f4392c6a6a692fdb37b79aab11` | `edce6832742f92a821ddfe33ffa2a0a1ea0c933ddc0a509a721ec37f48be29e0` |
| `717269ce447d2722faa84e6fdc5e97660981c26e` | `6d61387adde54859903946a6dd9dc13765324663cfe09f79b8f8d35bafcc1dc4` |
| `506a08eb4d50def9133896fe7d6d99b5a629cda0` | `e10dedde9ff0bd5ff6d215a3ee830bbde604a374c634e3598d216cedd7dbaf4a` |
| `f528744221077c59a7ba6a5eeb146ec7bda90ff5` | `26793309f4a823fb49d83710661fa201e2878af28017bcf915adb9c6dae9c01d` |

The simulator was built with Cargo release optimizations, `CARGO_PROFILE_RELEASE_LTO=false` and `CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16`. Result rows identify the runtime source and firmware SHA. The evidence summary also records script and UART hashes.

## Per-case results

### StickC

Arduino docs totals — DOCS-DEFECT 6, FAIL 1, PASS 37.

| Case | Status | Evidence | Runtime source | Firmware SHA-256 |
| --- | --- | --- | --- | --- |
| `axp192_m5stickc-1` | PASS | Two simulated battery levels changed the documented display versus default. Native 80×160, 1219 lit pixels, RGB CRC32 `0473f209` | `f52874422` | `62abe7c1a4643b924bf6469fcaaf98a01a0063561416b79d60b4d7e0e4fa66a4` |
| `axp192_m5stickc-2` | PASS | M5.begin addressed AXP192 and enabled the panel rails and backlight. Native 80×160, 0 lit pixels, RGB CRC32 `58a2b0f8` | `f52874422` | `3c0437148504055ffe11bbffddfa7d1104d747027d3ebbac7e3dc9b1425d66f4` |
| `axp192_m5stickc-3` | PASS | AXP192 shutdown removed panel power after an active frame. Native 80×160, 0 lit pixels, RGB CRC32 `58a2b0f8` | `f52874422` | `e8551a16821bac25ca7f86312cab9a7917f4e9cfd95e0894c1c8396f9860a058` |
| `axp192_m5stickc-4` | PASS | AXP192 LDO2 brightness followed the guest ramp. Native 80×160, 179 lit pixels, RGB CRC32 `5ca7b52c` | `f52874422` | `95a633e17fc1d78cd3284d3f342062501d5b964a8c3fedf4ac3df7482617eab6` |
| `axp192_m5stickc-5` | PASS | Guest ScreenSwitch changed the visible backlight across the two checkpoints. Native 80×160, 0 lit pixels, RGB CRC32 `58a2b0f8` | `f52874422` | `95fd553ae2bc19f2d55174d95d0778a2eff92f769e643c53390bb6030ff304fb` |
| `button-1` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 80×160, 237 lit pixels, RGB CRC32 `c961d988` | `f52874422` | `c150f847948b2c253c3933b0bf181bf0d44b44ed98c0fe3fd65edd983b0284f5` |
| `button-2` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 80×160, 283 lit pixels, RGB CRC32 `f4ea7e17` | `f52874422` | `5f02d5723562aba40e5e2de46297ecaff0a7b51861f3e0d89fc34095b7cc07c0` |
| `button-3` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 80×160, 261 lit pixels, RGB CRC32 `9630157a` | `f52874422` | `002cc4d1c785f570cf3b256818de6e07c0e3cdcae55b6f50b7c01783b448ce6a` |
| `button-4` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 80×160, 470 lit pixels, RGB CRC32 `6b043693` | `f52874422` | `b3da4f24e4a78d5f5f9a37cb54277a4e2be9b2ad86585e4438c472c4e15f684a` |
| `button-5` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 80×160, 739 lit pixels, RGB CRC32 `13badb7e` | `f52874422` | `56378790154b34df9e9ab2f90198f7d1057d2722c6ece60ed09c3e0639c336dd` |
| `button-6` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 80×160, 2000 lit pixels, RGB CRC32 `9feb0946` | `f52874422` | `87df458ce478e8f7794a05a6bce715579abee719d955cbc3367199c3fe8085aa` |
| `button-7` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 80×160, 211 lit pixels, RGB CRC32 `49ded953` | `f52874422` | `57a7a079c5e35d8b11be49766a4c1a00b9791c57dab063aea1b931586c723681` |
| `button-8` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 80×160, 488 lit pixels, RGB CRC32 `4eaae4ec` | `f52874422` | `919935a93ea4820d9f6972c408eb293c83ad9d6698212db5423ceaf7faa590ef` |
| `button-9` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 80×160, 301 lit pixels, RGB CRC32 `51f0834b` | `f52874422` | `b3d5e9f56cdc29d6c95e72b537b583ffbf0ca5ed743bd3d8a4bc1f49760b6541` |
| `imu-1` | PASS | Legacy sensor initialization returned success on UART. Native 80×160, 0 lit pixels, RGB CRC32 `58a2b0f8` | `f52874422` | `0b7c507d8ff9106bd55d5a75587031367af714ded24f71c715c6788d9a7bc05d` |
| `imu-2` | PASS | Distinct injected sensor inputs changed the application display versus idle. Native 80×160, 306 lit pixels, RGB CRC32 `d4ea0cd6` | `f52874422` | `3f6b09d6f83ad5e3f82e03487d70a6f3d790e1ca0f760a4a7d773f664043d26f` |
| `imu-3` | PASS | Distinct injected sensor inputs changed the application display versus idle. Native 80×160, 247 lit pixels, RGB CRC32 `2c1d427f` | `f52874422` | `7b3c5a1b585ee22264c9980bdb20cebf274d8fdfeba9e640e9d31db3371c6dd2` |
| `imu-4` | PASS | Distinct injected sensor inputs changed the application display versus idle. Native 80×160, 237 lit pixels, RGB CRC32 `3e911e5b` | `f52874422` | `8e4b1e1c3c497e8f3661cf5a7280d5c3ffba1f952794ef5ee385fda90a127505` |
| `imu-5` | FAIL | M5StickC 0.3.0 MPU6886.cpp:208–212 reads from 0x41 and interprets bytes 6–7 instead of bytes 0–1. Native 80×160, 228 lit pixels, RGB CRC32 `7bf5d411` | `f52874422` | `e9eb9003eeb49d9ef67d799d6244fec0d7afe4ced0f4e5f0e59543e7e160c5ee` |
| `lcd_m5stickc-1` | PASS | Visible pixel count or fill color matches the sketch operation. Native 80×160, 12800 lit pixels, RGB CRC32 `6c648fe0` | `f52874422` | `9a521939aeeb4b88c89585fa1038dc72568e4e702b46b0eeccec8f02773e351d` |
| `lcd_m5stickc-2` | PASS | The 22-character red-on-white text matches its glyph counts and wrap. Native 80×160, 1056 lit pixels, RGB CRC32 `5e896154` | `f52874422` | `fca5e0baa17c64644baddfe5a3275cb3d979a3d64719dfc73c2d4c693b55e9c0` |
| `lcd_m5stickc-3` | PASS | Default-font glyph counts and the documented cursor placement match. Native 80×160, 103 lit pixels, RGB CRC32 `1c84091c` | `f52874422` | `04a17a8f44ccfb06654fbb96723c165af1f2730e811d8e720e76c35aa7bcbd69` |
| `lcd_m5stickc-4` | PASS | Default-font glyph counts and the documented cursor placement match. Native 80×160, 169 lit pixels, RGB CRC32 `a053d439` | `f52874422` | `64d958579d303770542ba6ebd363abe7332c8a967caf213c90b47799b507dfa4` |
| `lcd_m5stickc-5` | PASS | Visible pixel count or fill color matches the sketch operation. Native 80×160, 1 lit pixels, RGB CRC32 `0dfd548f` | `f52874422` | `5063c3addace44f63a3719ac50b909630241cec5f8acf2e61788afa10176b115` |
| `lcd_m5stickc-6` | PASS | Visible pixel count or fill color matches the sketch operation. Native 80×160, 13 lit pixels, RGB CRC32 `ca5f451b` | `f52874422` | `2e20e12f29b6718acd4f70e4f90e426302807ff8f8f278b20b1a910ce247515d` |
| `lcd_m5stickc-7` | PASS | Visible pixel count or fill color matches the sketch operation. Native 80×160, 181 lit pixels, RGB CRC32 `d213684d` | `f52874422` | `dfa74ce39612c81ab04a79c29f99f1cdacd9274f1e3a165c629341186a8d1e90` |
| `lcd_m5stickc-8` | PASS | Visible pixel count or fill color matches the sketch operation. Native 80×160, 1194 lit pixels, RGB CRC32 `25a65894` | `f52874422` | `ac3c3d8cf7d8ea3ed96a769a2653f55b1b8716db0acd02f938cf8571faf8532f` |
| `lcd_m5stickc-9` | PASS | Visible pixel count or fill color matches the sketch operation. Native 80×160, 76 lit pixels, RGB CRC32 `deb47030` | `f52874422` | `15f0391f2b261f67e739588851ced896105b030251d73cfcb9d23128302b5337` |
| `lcd_m5stickc-10` | PASS | Visible pixel count or fill color matches the sketch operation. Native 80×160, 200 lit pixels, RGB CRC32 `6ed67251` | `f52874422` | `1366a2472d5c1313fb2a601228d187ed0e17d8c8a61830126daeaf4582ff695b` |
| `lcd_m5stickc-11` | PASS | Visible pixel count or fill color matches the sketch operation. Native 80×160, 180 lit pixels, RGB CRC32 `4e645375` | `f52874422` | `14bb2207f75e8deb927ca34d02e43e1585e7b31cb8d9aba411bd85aabca7feb0` |
| `mic` | PASS | Both PCM tones changed the guest waveform relative to silence. Native 80×160, 12557 lit pixels, RGB CRC32 `95f5dd26` | `f52874422` | `48b815dbca7c3b5cc40560724d9d4a520e5cc32fc38946ce69204dbd1e0357ac` |
| `pwm-1` | DOCS-DEFECT | `static/en/arduino/m5stickc/pwm.md:31,35`. LEDC 2.x functions removed by the pinned Arduino-ESP32 3.x package | `—` | `—` |
| `pwm-2` | DOCS-DEFECT | `static/en/arduino/m5stickc/pwm.md:63–64`. LEDC 2.x functions removed by the pinned Arduino-ESP32 3.x package | `—` | `—` |
| `rtc-1` | PASS | Guest RTC write changed the BCD calendar and virtual time advanced. Native 80×160, 0 lit pixels, RGB CRC32 `58a2b0f8` | `f52874422` | `ded3fde9e6bc00adf618e358462f0389088d2892b7e75a588a81454871ca7929` |
| `rtc-2` | PASS | Guest RTC write changed the BCD calendar and virtual time advanced. Native 80×160, 378 lit pixels, RGB CRC32 `f8b4c625` | `f52874422` | `bd136ff9ef068e4a4b8aa28127ee59ee7ba4cf37218f68e9cb4fc02ef19108f0` |
| `rtc-3` | PASS | Guest RTC write changed the BCD calendar and virtual time advanced. Native 80×160, 0 lit pixels, RGB CRC32 `58a2b0f8` | `f52874422` | `1c99d741b562331b96791dc26de0040331d91275440a36e7adb3aac8b07533e3` |
| `rtc-4` | PASS | Guest RTC write changed the BCD calendar and virtual time advanced. Native 80×160, 563 lit pixels, RGB CRC32 `d938eb90` | `f52874422` | `0550554cb2b60c693c4db55c44532673911f9a354ac00130182c3b8f70a65a5a` |
| `sh200q_m5stickc-1` | DOCS-DEFECT | `static/en/arduino/m5stickc/sh200q_m5stickc.md:23`. M5StickC 0.3.0 IMU does not expose I2C_Read_NBytes | `—` | `—` |
| `sh200q_m5stickc-2` | DOCS-DEFECT | `static/en/arduino/m5stickc/sh200q_m5stickc.md:37,50`. getGyroData accepts float pointers, example passes int16_t pointers | `—` | `—` |
| `sh200q_m5stickc-3` | DOCS-DEFECT | `static/en/arduino/m5stickc/sh200q_m5stickc.md:68,81`. getAccelData accepts float pointers, example passes int16_t pointers | `—` | `—` |
| `spm1423_m5stickc` | PASS | Both PCM tones changed the guest waveform relative to silence. Native 80×160, 12557 lit pixels, RGB CRC32 `9ff79229` | `f52874422` | `48b815dbca7c3b5cc40560724d9d4a520e5cc32fc38946ce69204dbd1e0357ac` |
| `system_m5stickc-1` | DOCS-DEFECT | `static/en/arduino/m5stickc/system_m5stickc.md:51–56`. standalone sketch omits Arduino loop() | `—` | `—` |
| `system_m5stickc-2` | PASS | System function displayed the BM8563 clock and its time advanced. Native 80×160, 1032 lit pixels, RGB CRC32 `6e6b2e2e` | `f52874422` | `1c53bcb79b7b0875669fa0aee1f8ab6e35cb42e3ff1933feb57600b08dc325f2` |
| `quickstart-helloworld` | PASS | The Hello World glyphs occupy the expected region seen in the product photograph. Native 80×160, 127 lit pixels, RGB CRC32 `afb49adb` | `f52874422` | `9f0e042130f8a3f37767395185b83fdb159c97a0e587f0b6aa701cfa3ad0f944` |
| `stock` | PASS | Stock menu changed after input; UART REPL read both buttons. Native 80×160, 7983 lit pixels, RGB CRC32 `bcada87c` | `f52874422` | `2463fc362f6acfacccb678a2c40aeb733e470ca793ec4a100d2e077baa641f03` |

### StickC Plus

Arduino docs totals — FAIL 1, PASS 28.

| Case | Status | Evidence | Runtime source | Firmware SHA-256 |
| --- | --- | --- | --- | --- |
| `button-1` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 135×240, 237 lit pixels, RGB CRC32 `4f211740` | `f52874422` | `888dea34801a605063e9e99732f5a0127a1bca87ee70f5994c62acadf7c1fc4f` |
| `button-2` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 135×240, 283 lit pixels, RGB CRC32 `796106b8` | `f52874422` | `e99974a1cd92896c0f27a1c72cfb0bc860aecd4f5e61728b5f5e215259fd6a76` |
| `button-3` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 135×240, 261 lit pixels, RGB CRC32 `d0c50962` | `f52874422` | `2ff6cf327405c27e3e7fef9fee0949b0e78d295e3065708b19bd4b62cafa174d` |
| `button-4` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 135×240, 470 lit pixels, RGB CRC32 `2141bf94` | `f52874422` | `83b15ce95278ec5f46e4846c84e30078274b53f0075150febc0ee2e82d9fb19c` |
| `button-5` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 135×240, 739 lit pixels, RGB CRC32 `0cd7d759` | `f52874422` | `a7250b1e2b22a2359cc43cd643c7616dc17a05e8ce5f8326848a483a68c0880c` |
| `button-6` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 135×240, 5720 lit pixels, RGB CRC32 `cdb8bae1` | `f52874422` | `96ae6add94683a15af10045e550e4566e24c1036d1776a51af2a9eee973c6d2f` |
| `button-7` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 135×240, 211 lit pixels, RGB CRC32 `29730ce2` | `f52874422` | `5ab4a468a4cdacdaee57c5951f8b965ddb8bb80bfec743dc75e5554100166666` |
| `button-8` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 135×240, 488 lit pixels, RGB CRC32 `8d3a1048` | `f52874422` | `192fcc2669ce61464e6e981e17997a2550d10725e8a7fd5d4ca68f1047757390` |
| `button-9` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 135×240, 301 lit pixels, RGB CRC32 `eec56209` | `f52874422` | `34d7fa4920d7cc28e66a089376c01933980691c04a0c9e13e0426d25c0c65467` |
| `buzzer` | FAIL | M5StickCPlus 0.1.1 Speaker.cpp:14,31 attaches GPIO2 at 0 Hz and calls the pin API with channel 0. Native 135×240, 0 lit pixels, RGB CRC32 `fae23ff0` | `f52874422` | `892df1588bc1e7b9b2830ecdd728ae5f33f794dc3e2728d74954d2e206be7d4b` |
| `display-1` | PASS | Visible pixel count or fill color matches the sketch operation. Native 135×240, 32400 lit pixels, RGB CRC32 `169842c2` | `f52874422` | `d12af2354876377a3047282ce27680d58095415fcac73e0156762b47212b04c8` |
| `display-2` | PASS | The 22-character red-on-white text matches its glyph counts and wrap. Native 135×240, 1056 lit pixels, RGB CRC32 `9d60731d` | `f52874422` | `9fc8f3567f62a2dbc4a2de298e91b121535df89d4cea8b3a52350bba09126b0a` |
| `display-3` | PASS | Default-font glyph counts and the documented cursor placement match. Native 135×240, 103 lit pixels, RGB CRC32 `c9885213` | `f52874422` | `fd8837bac9ab53bce5d5fb5f7ed853075e60ade4c9743c58161c9df65985c47b` |
| `display-4` | PASS | Default-font glyph counts and the documented cursor placement match. Native 135×240, 169 lit pixels, RGB CRC32 `e489d84c` | `f52874422` | `d45c1e56b89df6084ca9fc43af45dfc4c108fa9303a88512fd42daad6eee23ce` |
| `display-5` | PASS | Visible pixel count or fill color matches the sketch operation. Native 135×240, 1 lit pixels, RGB CRC32 `11593d20` | `f52874422` | `282561b7681766c8f0c71eb9b40ba0fb04fb1186c78215704f43736888024e5e` |
| `display-6` | PASS | Visible pixel count or fill color matches the sketch operation. Native 135×240, 13 lit pixels, RGB CRC32 `3687985a` | `f52874422` | `968032a976a6ab34d1fe84fbc725b4a13d139599a5c911f5c4bc71a28f7daf68` |
| `display-7` | PASS | Visible pixel count or fill color matches the sketch operation. Native 135×240, 181 lit pixels, RGB CRC32 `300bf109` | `f52874422` | `849e744121255d6a9f7856c40986f56b39482797c5300f21469758692ba4375a` |
| `display-8` | PASS | Visible pixel count or fill color matches the sketch operation. Native 135×240, 1194 lit pixels, RGB CRC32 `c4f9ae31` | `f52874422` | `f1ba0b496701350b9a4426070bff4e8a96bfde573eca0e95ab02ed44afd7894a` |
| `display-9` | PASS | Visible pixel count or fill color matches the sketch operation. Native 135×240, 76 lit pixels, RGB CRC32 `70d7ddb6` | `f52874422` | `c219690b582a16cf551e2ec801452c65cfbf4bc3ec3fde1295578d204a287cf9` |
| `display-10` | PASS | Visible pixel count or fill color matches the sketch operation. Native 135×240, 200 lit pixels, RGB CRC32 `d20f951a` | `f52874422` | `b8a766a3b6cc6fa57c164debf92ca145c61f772b8515c9845c6872c14657b000` |
| `display-11` | PASS | Visible pixel count or fill color matches the sketch operation. Native 135×240, 180 lit pixels, RGB CRC32 `437846bc` | `f52874422` | `a3118e2fa919326ae07f005d488e80a08116da235eb6d3f91a2799e6e0b17038` |
| `imu` | PASS | Distinct injected sensor inputs changed the application display versus idle. Native 135×240, 1141 lit pixels, RGB CRC32 `3f6d14d5` | `f52874422` | `7cd2b87fee0ef84064440dae694cf2a0fa7af0817059e90a1dba67cff7e07c0c` |
| `mic` | PASS | Both PCM tones changed the guest waveform relative to silence. Native 135×240, 32157 lit pixels, RGB CRC32 `8f3e80db` | `f52874422` | `cafb6ee55228503e6fcdb176de0dcb4630d3bc92531babe45099611f430604af` |
| `power-1` | PASS | Two simulated battery levels changed the documented display versus default. Native 135×240, 1219 lit pixels, RGB CRC32 `7e9510a7` | `f52874422` | `64c8255d142167fced09df1d287f26f7744924e1e3dc225bcbaf47ddb0bc1cbd` |
| `power-2` | PASS | M5.begin addressed AXP192 and enabled the panel rails and backlight. Native 135×240, 0 lit pixels, RGB CRC32 `fae23ff0` | `f52874422` | `091c5aafad0a5c4da5fd8e1f632dfebbc2b1370b013da3beb49ea96947a9c159` |
| `power-3` | PASS | AXP192 shutdown removed panel power after an active frame. Native 135×240, 0 lit pixels, RGB CRC32 `fae23ff0` | `f52874422` | `e739748b9774bc75318f3b727aba0ce1b057aca5617d8e979b4f63bb6dec5324` |
| `power-4` | PASS | AXP192 LDO2 brightness followed the guest ramp. Native 135×240, 179 lit pixels, RGB CRC32 `2fed8d55` | `f52874422` | `51b933338c0a917750102653ffd571fdc8c1d2b7f08fcf766c943a8fcaa1b8c6` |
| `power-5` | PASS | Guest ScreenSwitch changed the visible backlight across the two checkpoints. Native 135×240, 0 lit pixels, RGB CRC32 `fae23ff0` | `f52874422` | `0a87807d9c41e40d93cdef25205fed3ad1f7c515a4656a2ffc86476e84e78ad2` |
| `quickstart-display` | PASS | The color-fill sequence advances to the documented Display Test lettering. Native 135×240, 32400 lit pixels, RGB CRC32 `1d67dcb5` | `f52874422` | `7c66d997cd0976b3a0f24e3ca84dc815bc8e3c2f40a1fa6cc7ac0d0d70aa558c` |
| `stock` | PASS | Stock menu changed after input; UART REPL read both buttons. Native 135×240, 31021 lit pixels, RGB CRC32 `6f764c14` | `f52874422` | `6e82447cc87695703dc973a3d2bac00e34619bd5d011970df19f548923241cb2` |

### StickC Plus SE

Arduino docs totals — PASS 8.

| Case | Status | Evidence | Runtime source | Firmware SHA-256 |
| --- | --- | --- | --- | --- |
| `battery` | PASS | Two simulated battery levels changed the documented display versus default. Native 135×240, 1916 lit pixels, RGB CRC32 `c9dd8e4a` | `f52874422` | `76c34229b01a81e4401b7f3251e98cc86e818e375fdab8d2aced53660e5e1849` |
| `button` | PASS | Scripted GPIO input changed the documented button display versus idle. Native 135×240, 1032 lit pixels, RGB CRC32 `2fede38f` | `f52874422` | `4241d8be2461d6444c60d5cca6263417a303af6e9d0bda63ec26ce132b0b8612` |
| `display` | PASS | Native frame shows the expected 20×20 rectangles and circles at distinct checkpoints. Native 135×240, 32400 lit pixels, RGB CRC32 `b74986ae` | `f52874422` | `ec4b2bae22a0bc8516d9deba500b09a171d8e17c4a9a31df5841234ef3b1d730` |
| `ir_nec` | PASS | Decoded two expected NEC commands from the active-low GPIO9 PWM envelope. Native 135×240, 1969 lit pixels, RGB CRC32 `3d8c5a5a` | `f52874422` | `d73af24be9df6bde3c56db6fb1b3dc6081ee8aa092756dbcf939d2f632dcf65d` |
| `mic` | PASS | Distinct tone and silence frames; routed replay bursts (Hz, ms) [(738.1, 989.0)]. Native 135×240, 6233 lit pixels, RGB CRC32 `a5a45e24` | `f52874422` | `8e85f5f98100e55722fc419d760b3e76fac85127a12f78be3790990cb1319e1b` |
| `speaker` | PASS | Routed I2S piezo bursts (Hz, ms) [(7000.2, 99.9), (4000.0, 199.8), (7000.2, 95.9), (4000.0, 199.8), (6999.8, 97.1), (4000.0, 128.0)]. Native 135×240, 373 lit pixels, RGB CRC32 `f9ca3772` | `f52874422` | `3e16d4b062dd0103e0d43442e5706c61b3c9885719ccd5f065cc3726ef414f8a` |
| `wakeup` | PASS | Timed wake reset followed scripted button input and idle showed one boot. Native 135×240, 3997 lit pixels, RGB CRC32 `182770fd` | `f52874422` | `921ada10019f9e4c9990352d5edd0a94f191e77be3460cb8616c605e293fe0a8` |
| `quickstart-scrollgraph` | PASS | Six plotted colors and grid span the native display and advance across checkpoints. Native 135×240, 1851 lit pixels, RGB CRC32 `b5e3572c` | `f52874422` | `9b7bebf1eed5f422f22e513825da33c5b9ac8ca66ddc570bd8b06b078736e29a` |
| `stock` | PASS | Stock menu changed after input; UART REPL read both buttons. Native 135×240, 31022 lit pixels, RGB CRC32 `685e6dab` | `f52874422` | `0c7055bb8e64afe1d8fa4fd4bdc0961ca0d6366351aca5d6c83eaaf72155ee88` |

### StickC Plus2

Arduino docs totals — DOCS-DEFECT 1, PASS 10.

| Case | Status | Evidence | Runtime source | Firmware SHA-256 |
| --- | --- | --- | --- | --- |
| `battery` | PASS | Two simulated battery levels changed the documented display versus default. Native 135×240, 1046 lit pixels, RGB CRC32 `4ed97b18` | `f52874422` | `a9fcbe8608c541b9de39399e6d535c0e097752201e041cacc1f87ae9b0a7a09a` |
| `button` | DOCS-DEFECT | `static/en/arduino/m5stickc_plus2/button.md:33,36`. M5StickCPlus2 1.0.1 exposes BtnC, example calls BtnPWR | `—` | `—` |
| `buzzer` | PASS | Routed I2S piezo bursts (Hz, ms) [(10000.4, 99.9), (4000.0, 19.8), (10000.4, 99.9), (4000.0, 16.2), (10000.4, 99.9), (4013.6, 18.4)]. Native 135×240, 868 lit pixels, RGB CRC32 `f5f70cd7` | `f52874422` | `5582c83519a02dd7af8034b966065256cf90244129437c09bf0bd82cee66e6de` |
| `display` | PASS | Native frame shows the expected 20×20 rectangles and circles at distinct checkpoints. Native 135×240, 32400 lit pixels, RGB CRC32 `dfa326ea` | `f52874422` | `499ff2c14be1e2cc6424f4855bcec2ce01de37dca2c9b08efd796611b5b4fb4f` |
| `imu` | PASS | UART reports both injected accelerometer vectors and the idle control ran. Native 135×240, 1861 lit pixels, RGB CRC32 `ab003362` | `f52874422` | `abfb648a8e8493df181e049ce8d8f547bd1b211d29c0740fd4df329924778ddf` |
| `ir_nec` | PASS | Decoded GPIO19 NEC codes cb341111, ca351111, c9361111, c8371111, c7381111. Native 135×240, 2848 lit pixels, RGB CRC32 `bc0056a8` | `f52874422` | `c5648898ff9354b5c618d7bcb7b2f8454a786af134177ce985a04ed834cec055` |
| `led` | PASS | G19 SET/CLR edges observed through the GPIO controller. Native 135×240, 762 lit pixels, RGB CRC32 `4f757d51` | `f52874422` | `bc93ea3cf0931072c3d03a296cabc8a51c398be21296e0ac5285396392f40e34` |
| `mic` | PASS | Distinct tone and silence frames; routed replay bursts (Hz, ms) [(732.9, 1049.2)]. Native 135×240, 2774 lit pixels, RGB CRC32 `df8a0fab` | `f52874422` | `fb7b241abbb1168d8f97286b4f5ab1ad0c37a7efb9c9205f18e443547d095791` |
| `rtc` | PASS | Virtual Wi-Fi/SNTP populated the hardware RTC. Native 135×240, 1392 lit pixels, RGB CRC32 `92790915` | `f52874422` | `b7c2850ec9a3d3be1a46722261207e46ceba6976991e9cc78f56eaa1b25ea055` |
| `wakeup` | PASS | Timed wake reset followed scripted button input and idle showed one boot. Native 135×240, 1106 lit pixels, RGB CRC32 `990cf002` | `f52874422` | `83c12e633a21f5bf55a2dc8ae8933d1103312e4fa00dca190116544154d693a3` |
| `quickstart-display` | PASS | Native frame shows the expected 20×20 rectangles and circles at distinct checkpoints. Native 135×240, 32400 lit pixels, RGB CRC32 `dfa326ea` | `f52874422` | `b660a3cf47a64ed3e5506e164f4ca8f1b431c3f77c79693b1c9e5a074b3fba35` |
| `stock` | PASS | Stock menu changed after input; UART REPL read both buttons. Native 135×240, 31106 lit pixels, RGB CRC32 `7f594e68` | `f52874422` | `712fd8ca7d232ca84b1214610b7b7933bca4f19233258736d0db33147b4342dc` |

### M5Stick

The product has a catalog factory image and no dedicated Arduino docs suite.

| Case | Status | Evidence | Runtime source | Firmware SHA-256 |
| --- | --- | --- | --- | --- |
| `factory` | FAIL | Factory app reports MPU9250 probe FF and the visible OLED stays blank. Native 64×128, 0 lit pixels, RGB CRC32 `db13c854` | `f52874422` | `84228dfb6f0dd9b84b63c33f93a53545d8d43658893f432e3eaf4313923bffca` |
| `probe` | PASS | Controller probes check sensor input readback and native framebuffer. Native 64×128, 128 lit pixels, RGB CRC32 `78746a81` | `f52874422` | `8d13d287e18c56a8a27e5bf1617dca81a1c6d847dc302f034f09854753c184d0` |

### M5StickT2

The product has a catalog factory image and no dedicated Arduino docs suite.

| Case | Status | Evidence | Runtime source | Firmware SHA-256 |
| --- | --- | --- | --- | --- |
| `factory` | FAIL | Factory app renders its splash and prints error=2 without a complete VoSPI frame. Native 135×240, 31249 lit pixels, RGB CRC32 `1be87970` | `f52874422` | `bb33ffd41f9c6f9235b2fb44eac893b7ce6f70879f48eed9cb1ff75ef9419cd7` |
| `probe` | PASS | Controller probes check sensor input readback and native framebuffer. Native 135×240, 16200 lit pixels, RGB CRC32 `f63c63b5` | `f52874422` | `8d13d287e18c56a8a27e5bf1617dca81a1c6d847dc302f034f09854753c184d0` |

## Observations and unresolved behavior

- Milestones were pushed separately for Plus2 at `5139e9dad0faa7f4c08b40c5c7c2d6d36d2ac4d8` and Plus SE at `1a6a8bae16d50b2ddf4da52f8df2c2acd1504089`. The Plus SE matrix passed again after model unification.
- The four official UIFlow2 images rendered their home screen. A scripted button changed the menu frame and UART0 read each button as released, pressed and released. Plus2 reports board ID 5, Plus and SE report ID 4, and StickC reports ID 3 through the guest.
- StickC's Hello World was compared against the product photo. Plus SE's six-color scrollgraph matched the photographed layout after accounting for glass orientation. Plus's quickstart showed the full color fill and later the Display Test lettering. Plus2 showed the documented moving colored rectangles and circles.
- The Classic Core subset also checked both Core2 PMIC revisions. The first legacy Core2 battery trial used the AXP2101 script shape and was rejected. The corrected AXP192 trial used 3678 mV at −150 mA, 4096 mV at +150 mA and idle. Each rendered a distinct frame after 23 or more AXP192 I²C reads.
- The full Core2 v1.1 replay had one microSD failure with the shared Basic seed. The retest used the Core2-specific 320×240 seed and passed both image checkpoints, the absent-card control and the persisted write.
- AXP192 LDO2/LDO3 checks cover initial power, brightness ramps, panel off and key restart. The first power-on replay reported reset at its final time bound. Following the scheduler fix, both guests reset at the scripted 4.100 s event and printed a second ROM boot marker.
- StickC's installed M5StickC 0.3.0 library starts the MPU6886 temperature burst at register 0x41 and decodes bytes 6–7. The original sketch frame was identical at both temperatures and idle. A separate stock UART probe read `0000`, `f99e` and `0cc4` via hardware I²C, which proves the simulator's register path.
- StickC Plus's installed M5StickCPlus 0.1.1 `Speaker.cpp:14,31` requests 0 Hz for attach and uses the old channel with the pin-based tone API. The original sketch emitted zero GPIO2 PWM updates. A separate stock UART PWM control exercised GPIO2 at 3993.610 Hz and 50% duty. [Arduino-ESP32 LEDC implementation](https://github.com/espressif/arduino-esp32/blob/3.2.1/cores/esp32/esp32-hal-ledc.c#L172)
- Plus SE and Plus2 each rendered distinct waves for 733 Hz, 1234 Hz and silence. Both captured a virtual replay of the 733 Hz input. Plus SE's GPIO9 NEC decoded (0, 85), (1, 86) and (2, 87). Plus2's GPIO19 transmitted extended NEC address 0x1111.
- Plus2's original RTC example associated with an isolated virtual network and used DHCP, DNS and SNTP. Its BM8563 returned `25-11-24T16:00:09`. The disconnected control retained the default 2024 calendar.
- M5Stick factory firmware prints `mpu9250 addr: FF` and ends on a blank OLED. The legacy I²C command list reaches START with no address byte observed at the modeled FIFO. The separate exact-board controller probe read MPU9250 and AK8963 IDs `71` and `48`, two distinct motion and magnetic samples, two IP5306 battery indications and a 128-pixel SH1107 pattern.
- StickT2 factory firmware displays its splash and prints `M5StickC initializing...OK` followed by repeated `error=2`. The separate controller probe verifies Lepton reset and CCI, four ordered VoSPI segments for each complete 160×120 frame, both scene digests, encoder positions +5, −3 and zero, and 16,200 colored ST7789 pixels. Its initial single-allocation drawing attempt hit the guest heap limit. Row-sized rendering verified the display without changing the simulator.
- M5Stick GPIO26 buzzer, GPIO17 IR, GPIO19 LED and original factory input behavior remain NOT RUN as controlled end-to-end operations. StickT2's original thermal UI and button behavior remain incomplete. Physical sensors, optics, thermal measurements, audio and actual power behavior were NOT RUN. The shared receiver checks below exercise raw PDM and a simulated external IR receiver's digital output.

## NEC receive and raw PDM

The StickC boards carry onboard IR emitters. The separate ESP-IDF fixture attaches an external Unit IR-style digital receive signal to Grove G33 and leaves the documented transmitter wiring intact. The same fixture uses the built-in SPM1423 digital pins G0 and G34 for raw PDM. It reuses the LX6-A controller implementation and runs independently of the stock and Arduino firmware. [Unit IR pin map](https://docs.m5stack.com/en/unit/Unit_IR)

| Board | External RMT RX | Raw PDM |
| --- | --- | --- |
| `stickc` | PASS, `aa55ff00`, `a956fe01` and idle | PASS, low/high/mixed DMA words and 20,480 idle zero words |
| `stickc-plus` | PASS, `aa55ff00`, `a956fe01` and idle | PASS, low/high/mixed DMA words and 20,480 idle zero words |
| `stickc-plus-se` | PASS, `aa55ff00`, `a956fe01` and idle | PASS, low/high/mixed DMA words and 20,480 idle zero words |
| `stickc-plus2` | PASS, `aa55ff00`, `a956fe01` and idle | PASS, low/high/mixed DMA words and 20,480 idle zero words |
| `stickt2` | PASS, `aa55ff00`, `a956fe01` and idle | PASS, low/high/mixed DMA words and 20,480 idle zero words |

## Shared models and regression

LX6-B merges the LX6-C branch. The combined tree uses LX6-C's AXP192 register model for Core2 and all applicable Stick profiles, with Stick startup rails, VBUS, power-key IRQ and shutdown extensions. It extends LX6-C's IP5306 gauge with the M5Stick boost and supply behavior. Both profiles retain their own reset defaults. The shared SPI FIFO repeat fix is implemented once and coexists with sub-byte reads and shared display-data routing. Continuous I²S-to-DAC for the Core boards and GPIO-routed piezo audio for the Stick boards use the same I²S controller.

One-second instruction sentinels matched the LX6-A base on both chips. The classic run executed 4,342,917 + 431,305 instructions and the S3 run executed 2,658,432 + 1,084,186. UART output matched byte for byte in each pair.

The original LX6-A receiver fixture also passed with the combined binary. The Basic v2.7 cyclic DAC capture reproduced a 500 Hz pattern at 32 kHz.

The batch reuses the unified MPU6886 and BM8563. SH1107, MPU9250/AK8963, the Lepton model and NEC decoding are shared modules. The classic FRC2, GPIO/I²S routing and powered-board wake adapter are available to sibling LX6 batches. Cardputer-ADV uses the shared NEC decoder.

- cores3 — 15/15 PASS at `f52874422`.
- adv — 11/11 PASS at `f52874422`.
- atom-lite — PASS 7.
- atom-matrix — PASS 8.
- atom-matrix-v11 — PASS 8.
- atomu — FAIL 1, PASS 2 (stock-startup FAIL).
- atom-echo — DOCS-DEFECT 3, FAIL 1, PASS 3 (quickstart-echorest DOCS-DEFECT, quickstart-playmusic DOCS-DEFECT, quickstart-recordplay DOCS-DEFECT, stock-startup FAIL).
- basic-v27 — PASS at `506a08eb4` (DOCS-DEFECT 1, PASS 9). `imu` DOCS-DEFECT — Fixture assignment points Basic at m5core/imu.md line 9, which targets Gray. K001-V27 Basic has no onboard IMU..
- core2 — FAIL at `506a08eb4` (FAIL 1, PASS 14). `microsd` FAIL — missing differentiated decoded images or no-card state.
- core2-microsd-retest — PASS at `f52874422`. Two guest-decoded images, missing-card control and exact persisted WriteTest.txt after the Core2-sized PNG seed was supplied.
- core2-power-stock — PASS at `f52874422` for battery PASS, stock PASS.
- core2-axp192-power-stock — PASS at `f52874422` for battery PASS, stock PASS.
- cargo — 1996 passed and 7 failed at `f52874422`. The same failed cases reproduce at the LX6-A base.
- clippy — native PASS and wasm32 PASS.

Workspace exceptions are `hello_world_p4_rev3_smp`, `hello_world_p4_smp`, `hosted_p4`, `hosted_p4_rev3`, `hosted_rawtp_rx`, `hosted_rawtp_tx`, `wifi_sta_is_refused_where_it_does_not_work_yet`.

## Reproduction and rollback

Build the merged branch with `cargo build --release -p esp32sim --bin esp32sim`. The Stick runner takes the plan directory containing the Arduino inventory and merged firmware, the stock artifact and the classic ROM ELF. Repeat for each CLI board alias. Use `--probe-stock ATOM_LITE_BIN` for the two original factory boards. The checker reads the UART, panel, waveform and register traces.

```sh
python3 tools/run-lx6-stick.py stickc target/release/esp32sim PLAN STICKC_BIN ROM OUT
cargo test --release --workspace --no-fail-fast -- --include-ignored --skip external_
cargo clippy --workspace --all-targets -- -D warnings
cargo clippy -p esp32sim-wasm --target wasm32-unknown-unknown -- -D warnings
```

Use the saved base revision for a rollback of the whole batch. The fork branch can be reviewed independently before integration. Raw captures and the supplied firmware and ROM files were kept outside Git. The published summary contains protocol values and digests, with host paths and raw machine logs omitted.
