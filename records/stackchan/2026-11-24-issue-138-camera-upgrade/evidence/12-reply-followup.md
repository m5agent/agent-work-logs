Thanks — both of these have concrete answers, and they separate cleanly into "not obtainable" and "obtainable with a config change plus validation".

**1. Sub-board schematic, full 24-pin pinout, rail specifications**

I can't obtain or release those documents. The public K151 documentation is an 11-page set (7 CoreS3 pages + Adapter/Power/Ring/Touch); it ends at `J2` and has no camera/sensor sub-board page or BOM. It gives the `J2` signal groups and the rail topology — `AVDD`/`DVDD` from the AXP2101 BLDO rails, `VDDCAM_3V3` from an AXP2101 ALDO rail, and the 20 MHz oscillator `X2` fed from `VDDCAM_3V3` — but it does not give the pin 1–24 assignment, the per-rail current budget, or the sub-board decoupling. The only pin number annotated on the public page is `CAM_MCLK` → `J2` pin 12.

The route I would use is a direct M5Stack support/FAE request (or distributor ticket) with the SKU and unit batch, asking for: camera/sensor sub-board schematic + BOM, `J2` mating pinout with pin numbers, and per-rail voltage/current limits. It may be supplier-NDA material, so support may only share connector-level information; I can help review what they provide, but I can't extract it from the public docs.

**2. Is the existing GC0308 VGA mode enough for 640×480?**

For the official StackChan firmware (v1.6.2, `esp_video` 2.5.0 + `esp_cam_sensor` 2.6.0), enabling the VGA mode is necessary and sufficient for the **capture size itself**, but not by itself a guarantee of reliable audio/avatar operation. The sensor table already has `640×480@16` YUV422 (UYVY) at 20 MHz, and the app takes width/height from `VIDIOC_G_FMT`; the PSRAM frame copy, preview conversion and JPEG encoder all size from the format rather than a hard-coded 320×240. So no capture-pipeline code change is needed for `camera.capture()` to return 640×480.

In `firmware/sdkconfig.defaults`, replace:

```
CONFIG_CAMERA_GC0308_DVP_YUV422_320X240_20FPS=y
```

with:

```
CONFIG_CAMERA_GC0308_DVP_YUV422_640X480_16FPS=y
```

and make sure `CONFIG_CAMERA_GC0308_DVP_DEFAULT_FMT_YUV422_640X480_16FPS=y` actually wins. If you leave both modes enabled, or reuse a stale `sdkconfig`, the default-format choice can still select 320×240; removing the 320 mode or deleting the old `sdkconfig` avoids that.

The parts I would validate before calling it reliable:

- **PSRAM headroom.** At VGA YUV422 one frame is 614,400 bytes. The current path can hold a DVP buffer + captured copy + RGB565 preview = ~1.8 MB, versus ~0.46 MB at QVGA. It fits in 8 MB, but measure the largest free PSRAM block after avatar assets, LVGL, audio and Wi-Fi are up, not just at boot.
- **Bandwidth/CPU.** 640×480@16 is ~9.8 MB/s of camera data versus ~3.1 MB/s at 320×240@20, plus a 640×480 YUV→RGB conversion for preview and a larger JPEG. This is the part that can disturb audio and the avatar; test with audio playing, animation running and Wi-Fi connected, not only a still capture.
- **Streaming vs stills.** The DVP path currently requests one V4L2 buffer. That is fine for a still, but continuous VGA streaming serializes capture and consumer and will drop frames unless you change the buffering.
- **Preview.** The display is 320×240 and `SetPreviewImage` scales by width, so 640×480 displays at 320×240 without code changes; check LVGL's downscale and the 6 s preview lifetime do not add a second full-size allocation you did not expect.

If you use the Arduino/`esp32-camera` example instead of the StackChan firmware, two extra changes are required: set `.frame_size = FRAMESIZE_VGA` **and** change/remove the `set_framesize(..., FRAMESIZE_QVGA)` call in `setup()`, otherwise it resets to QVGA; and note that `pushImage(0, 0, 320, 240, fb->buf)` is a top-left crop at VGA, not a scaled preview. Two RGB565 VGA PSRAM buffers are ~1.2 MB, so keep `fb_count=2` or switch to JPEG; the GC0308 driver clamps anything above VGA to VGA, so 640×480 is its maximum there.

**Evidence class: code-level verification**, plus one separate virtual-device data point. Sources: `m5stack/StackChan@28b9f0c8` `firmware/sdkconfig.defaults:58-59`, `firmware/main/hal/board/stackchan.cc:632-675`, `firmware/main/hal/board/config.h:44-62`; `78/xiaozhi-esp32@49b4380b` `main/boards/common/esp_video.cc:178-197,302-304,425-442,790-800,960-964`; `esp_cam_sensor 2.6.0` `sensors/gc0308/Kconfig.gc0308:48-61` and `gc0308.c:39-77`; `esp_video 2.5.0` `src/device/esp_video_dvp_device.c:30-34`; official StackChan camera example at docs.m5stack.com/en/arduino/stackchan/camera. On the AtomS3R-CAM virtual profile (same GC0308 DVP model, `esp32-camera` path) `camera.init(framesize=VGA)` produced 640×480 / 614,400-byte frames matching the host oracle (record: `m5agent/m5stack-esp-emulator` commit `ee3290428`, `docs/evidence/2026-11-02-atoms3r-cam-geometry`); that confirms the sensor mode, not StackChan's `esp_video` path.

**Not covered:** no K151 hardware (`NOT RUN`), so no actual J2 continuity, rail current or thermal measurement. StackChan virtual-device VGA is also `NOT RUN`: the local StackChan profile models the camera as a fixed 320×240 DVP frame source (the GC0308 geometry binding is wired only for AtomS3R-CAM), so it cannot exercise a VGA StackChan image without changing the emulator model. I did not build a VGA image or measure the audio/PSRAM impact. The sub-board pinout and rail limits remain the blocking unknowns for the adapter.

Full follow-up notes: https://github.com/m5agent/agent-work-logs/tree/98131d7e66b17dcf4ccf286af5f1ab5da84e88c3/records/stackchan/2026-11-24-issue-138-camera-upgrade
