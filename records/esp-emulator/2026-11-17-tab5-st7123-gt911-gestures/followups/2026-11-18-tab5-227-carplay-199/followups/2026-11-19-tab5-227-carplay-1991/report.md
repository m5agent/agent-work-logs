# #227 原版冷启动与 GT911 输入

原问题在 `bsp_get_board_version()` 探测不到触摸器件时进入断言和复位循环。Device Service 1.99.1 以原生 DSI 与已准入 GT911 Part 复验同一原版。上一轮 1.99.0 使用相同后端与 Part，保存了该原版的启动和触摸对照。 [原始问题](https://github.com/m5agent/m5stack-esp-emulator/issues/227) · [1.99.0 验证](https://github.com/m5agent/agent-work-logs/blob/8c4997eb70ee10b8af175f631c2d9fa561159fd4/records/esp-emulator/2026-11-17-tab5-st7123-gt911-gestures/followups/2026-11-18-tab5-227-carplay-199/README.md)

macOS arm64 的固定执行源码为 `c9ec0f274579b78d87a4a301147f351e8b7a48fa`，OpenAPI 为 1.99.1。执行后回读的 `main` `9331d771e927b18ce913cf6132bf821df1269b60` 与执行源码只差三份状态文档。后端、板型 Part、ROM、eFuse 输入与 C6 固件的完整 SHA-256 见摘要。 [main](https://github.com/m5agent/m5stack-esp-emulator/tree/9331d771e927b18ce913cf6132bf821df1269b60) · [精确工件身份](evidence/carplay-227-1991.summary.json)

## 同一原版普通会话

1. 用已固定的 Espressif esp-emu 1.1.0 和 GT911 Part 启独立 `platform/tools/serve.py`。以 `M5_TAB5_DSI_EMULATOR` 与 `M5_TAB5_GT911_PART` 指定工件，令 `M5_TAB5_DSI_BOARD=gt911-ili9881c`，并把规范化 Flash SHA 加入 `M5_TAB5_DSI_FIRMWARE_SHA256S`。
2. 通过 `POST /api/v1/artifacts`、`POST /api/v1/firmware/import` 和 `POST /api/v1/sessions` 创建 `device_id=tab5`、`runtime=qemu` 会话。2,221,360 字节原版仅以 `0xff` 补齐 16 MiB。串口显示应用从 `0x10000` 加载，API 与 ZIP 应用身份一致。本次启动无 ELF、无调试器。
3. 使用 `frame.png?max_age_ms=0&orient=panel` 取得 720×1280 原生 DSI 主页，另三次重新取帧哈希一致。以 `/input` 点击面板坐标 `(320, 500)` 作空白对照，主页不变。点击 `(640, 160)` 显示 `Clear phone pairing?`。每次点击均 `13/13` GT911 报告获实际来宾确认。
4. 观察至 22.419 秒，最后仍为原版确认框，P4 与 C6 保持同次进程。UART 有一个 ROM 启动标记、没有软件复位。日志未出现旧的 `bsp_get_board_version` 断言、非法指令地址或重启标记。主画面和确认框分别有 48 色和 71 色，各有 921,600 个非黑像素。
5. 停机前通过 `/evidence?include=manifest,serial,frames,logs,events` 取得 41,911 字节证据 ZIP。CRC 和五个清单成员逐字节校验，ZIP 中确认框与实际取帧哈希一致，串口与 API 取样一致。用 `DELETE ?purge=0&retain_flash=0` 停机，历史可读、Flash 释放、零租约，隔离进程均退出。原版、规范化输入、运行时与固定工件停机后哈希一致。

本轮覆盖 #227 所报同一原版的 BSP 板型探测和首次出帧，并以同会话的应用交互确认可用。USB DWC 枚举、手机握手、GT911 复位引脚、其他板型、外部网络、浏览器与实体硬件未执行。未确认清除配对。无源码或常驻服务改动。

原始帧、串口、日志与 ZIP 保持私有。公开摘要保留执行时序、工件哈希与清理状态。 [脱敏证据摘要](evidence/carplay-227-1991.summary.json)
