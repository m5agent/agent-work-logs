Thanks for the detailed question — and welcome to StackChan. I checked the published StackChan Core / CoreS3 schematic pages, the current firmware source and the camera/sensor component tables. Short answer: there is no confirmed drop-in higher-resolution module for K151 today, but the host side is a generic 8-bit DVP + SCCB interface, so a swap is technically plausible. The missing piece is the camera sub-board's 24-pin FPC pinout and BOM, which M5Stack has not published.

**1. Is there an electrically and mechanically compatible replacement?**

No public one that I can confirm. The published schematic shows:

- `J2` is a 24-pin `AFC34-S24FIA-00` camera/sensor sub-board connector carrying `CAM_D2–D9` (8-bit parallel data), `CAM_PCLK`, `CAM_VSYNC`, `CAM_HREF`, `CAM_RST`, `CAM_PWDN`, `CAM_MCLK`, `I2C_SYS_SDA/SCL`, plus `AVDD`, `DVDD` and `VDDCAM_3V3`.
- `CAM_MCLK` is a fixed 20 MHz from oscillator `X2` (through `R31` 51 Ω); the ESP32-S3 does not generate it, and the firmware leaves `CAMERA_PIN_XCLK` as `NC`.
- The firmware initialises the camera as 8-bit DVP, SCCB on the shared system I2C at 100 kHz, with `CAMERA_PIN_RESET` / `CAMERA_PIN_PWDN` also `NC`. `CAM_RST` is wired to the AW9523B IO expander (`P1_0`) if a reset pulse is ever needed.

So a candidate must be a 3.3 V-class DVP sensor module that accepts a 20 MHz XCLK input, uses an SCCB address that does not collide with the on-board devices (GC0308 is `0x21`; OV2640 `0x30` and OV3660/OV5640 `0x3C` are free), and matches the FPC mapping. The mapping is exactly what is not public: the schematic ends at `J2`, and the sub-board schematic/BOM is not in the published set. Without buzzing out `J2` or getting the sub-board drawing, "compatible" cannot be stated honestly.

**2. Would a custom adapter be required?**

Most likely yes, unless the candidate happens to share the same 24-pin order and rail arrangement. The connector carries three separate rails (`AVDD`, `DVDD`, `VDDCAM_3V3`) rather than a single 3.3 V feed, so an adapter has to reproduce whatever the sub-board expects. A passive re-wiring adapter works only if pin order, rails, reset polarity and XCLK all match; modules that expect one 3.3 V supply and generate their own core rails may need regulation on the adapter. The lens height/FOV fit behind the face is also not covered by the published schematic set and needs a physical check.

**3. Can the proximity and ambient light sensors be retained?**

The LTR-553ALS-WA is documented for StackChan (there is an official Arduino example using the LTR5XX library), and the product docs group it with the camera as a sub-board device; the main-board schematic shows neither part, only `J2`. So if the camera/sensor sub-board is replaced, the LTR-553 goes with it unless the new board carries the same part. Two caveats: the sub-board BOM is not published, and at least one K151 owner reported `0x23` not ACKing (#77, closed without a maintainer answer), so check your own unit before assuming it will be lost.

**4. What is the maximum realistic camera resolution on the ESP32-S3?**

There are three different ceilings:

- **Sensor capability:** OV2640 1600×1200, OV3660 2048×1536, OV5640 2592×1944 (esp32-camera sensor table).
- **The current factory stack** (`esp_video` 2.5.0 + `esp_cam_sensor` 2.6.0, DVP tables): OV2640 tops out at JPEG 1600×1200@12, OV3660 at JPEG 1280×720@12, and OV5640 at only 800×600@10. The OV5640 DVP entry is narrower than OV2640's, so on the AI.AGENT path OV5640 would give you less than OV2640 unless the stack is changed.
- **Memory/throughput:** with 8 MB PSRAM, one RGB565 frame at 1600×1200 is ~3.8 MB; 2592×1944 RGB565 is ~10 MB and cannot fit. 5 MP is only a JPEG proposition, and esp32-camera itself warns that YUV/RGB capture strains PSRAM and can drop data, especially with Wi-Fi active, recommending JPEG instead.

Also note the current pipeline is 320×240 YUV422 (the official Arduino example is `FRAMESIZE_QVGA` as well); even the stock GC0308 supports 640×480@16 in `esp_cam_sensor`, so the first "upgrade" is a firmware config change, not hardware.

For StackChan specifically, I would treat VGA-class as comfortable and UXGA-class JPEG as the practical ceiling. The bottleneck is the shared PSRAM/CPU/audio/Wi-Fi budget, not the sensor's megapixel count. The community hit the same wall in #70: on-device face detection alongside audio, avatar and networking was not stable, and they moved recognition to a host.

**5. Is M5Stack considering an official camera upgrade?**

I cannot confirm any plan. I found no public roadmap item or repository discussion for a camera upgrade, and I am not able to speak for M5Stack's product plans — that question is best put to M5Stack support/FAE.

**Has anyone done it?** I found no public report of a GC0308 → OV2640/OV3660/OV5640 swap on StackChan. The closest threads are #70 (offload vision to a host) and #103 (camera capture vs. audio), neither a hardware swap.

**Evidence class: code-level verification.** Basis: the published StackChan Core / CoreS3 v1.0 schematic pages, `m5stack/StackChan` @ `28b9f0c` (v1.6.2 main), `esp_video` 2.5.0 / `esp_cam_sensor` 2.6.0 / `esp32-camera` 2.1.8 tables, and the official StackChan camera/LTR553 documentation.

**Where to look**

- Schematic: StackChan Core page, `J2` 24-pin camera/sensor connector, `X2` 20 MHz, AW9523B `P1_0` = `CAM_RST`.
- Firmware: `firmware/main/hal/board/config.h:42-62`; `firmware/main/hal/board/stackchan.cc:632-675`; `firmware/sdkconfig.defaults:58-59` (`CONFIG_CAMERA_GC0308_DVP_YUV422_320X240_20FPS=y`).
- Sensor ceilings: `esp_cam_sensor` v2.6.0 `sensors/{gc0308,ov2640,ov3660,ov5640}` format tables; esp32-camera README sensor table and PSRAM/format notes.
- Docs: docs.m5stack.com StackChan camera example (`FRAMESIZE_QVGA`) and LTR553 example.

**Not covered**

- Hardware validation `NOT RUN`: no K151 unit here, so no electrical measurement, no FPC continuity check, no lens/mechanical fit, no thermal check.
- Virtual-device validation was not used. The local StackChan virtual profile exists (ESP32-S3, 320×240 display, simulated peripherals), but its camera path is a modelled GC0308 DVP frame source; it cannot represent a different physical sensor's pinout, rails, SCCB ID or optics, so it would only re-confirm the existing path.
- I did not build an image with another sensor driver enabled; whether `esp_video`'s V4L2 path accepts the JPEG DVP tables in this firmware was not tested.
- The sub-board schematic/BOM is not public; the `J2` pin-function list comes from main-board net names, not from the sub-board.
- LTR-553 population on K151 revisions is not confirmed.

If you are willing to open the unit and photograph / buzz out the 24-pin FPC (pin 1 and the rails especially), that would turn this from "plausible" into a concrete adapter design. And if you mainly need better recognition rather than more pixels, the #70-style host offload is the lower-risk path.

Full analysis and excerpts: https://github.com/m5agent/agent-work-logs/tree/main/records/stackchan/2026-11-24-issue-138-camera-upgrade
