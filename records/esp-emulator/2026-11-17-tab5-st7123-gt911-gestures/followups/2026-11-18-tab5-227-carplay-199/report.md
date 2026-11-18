# #227 原版启动和 GT911 应用输入

原 issue 在 esp-emu 0.50.0 缺少 ST7123 与 GT911 备用地址设备时，CarPlay
原版在 `bsp_get_board_version` 的板型探测处断言，并反复启动。
[原版历史对照](https://github.com/m5agent/m5stack-esp-emulator/blob/218106fac28258325bed4a58091cf1217f67252f/docs/evidence/2026-11-16-tab5-original-startup/README.md)
保留了旧版板型探测和 1.0.0 的独立 CSR 阻断。
[既有原版及数据面证据](https://github.com/m5agent/m5stack-esp-emulator/blob/218106fac28258325bed4a58091cf1217f67252f/docs/evidence/2026-11-17-tab5-st7123-gt911-gestures/README.md)
用独立 ESP-IDF 探针对照了 HP I²C1 的坐标读取、GPIO23 IRQ 与释放，并验证了
CarPlay 原版在旧版隔离服务上的输入。此次复验接续实际已交付的 1.99.0 配置。

## 执行路径

启动独立状态目录和独立监听的 `platform/tools/serve.py`。用固定 SHA 的
esp-emu 1.1.0 和 GT911 Part 设置 `M5_TAB5_DSI_EMULATOR`、
`M5_TAB5_GT911_PART`，板型为 `gt911-ili9881c`，将规范化 Flash SHA
加入 `M5_TAB5_DSI_FIRMWARE_SHA256S`。ROM、eFuse 像和 C6 固件分别与摘要
固定哈希核对。执行源码、OpenAPI、Tab5 设备矩阵和常规取帧入口均对应所声明的
发布源码。新状态只复用逐字节校验的只读二进制缓存副本。服务通过普通 API
重新接受原始上传、导入并创建新会话。

走 `POST /api/v1/artifacts`、`POST /api/v1/firmware/import` 和
`POST /api/v1/sessions`。创建使用 `device_id=tab5` 和 `runtime=qemu`，
无匹配 ELF、无调试、原应用未修改。用 `GET /api/v1/sessions/{id}/frame.png`
明示 `max_age_ms=0`、`orient=panel`。连续确认同一 P4 和 C6 伴生进程。

| 检查 | 实际结果 |
| --- | --- |
| 原版和规范化镜像 | 2,221,360 字节原版仅补 `0xff` 至 16 MiB，执行时应用字节保持不变 |
| 普通启动与无 ELF 取帧 | 1.538 秒读到 720×1280 主页，SHA `b9caf8f325d9b9ec1ee5d7ae3b49f3c709d584b0a5dce54d2ffd2fc62708f767` |
| 无操作对照 | `POST /api/v1/sessions/{id}/input` 点击 `(320, 500)`，13/13 GT911 报告获确认，无画面变化 |
| 原版应用操作 | 同一 API 点击 `(640, 160)`，13/13 GT911 报告获确认，原版清除配对确认弹窗；未确认清除 |
| 旧问题再现检查 | 22.634 秒观察窗，1 次 ROM 启动，0 次软件复位，无旧板型探测或旧 abort 标记 |
| 同会话证据与清理 | 41,886 字节 ZIP，通过 CRC 和清单 5 项校验，停止后会话可读、Flash 释放、0 租约且全部自有进程退出 |

本轮结论覆盖 #227 所报同一原版在 GT911／ILI9881C 上的板型探测、启动显示和
已执行的 BSP 输入链路。GT911 Part 的现有配置只列 SCL、SDA 和 INT，
本轮无硬件复位引脚观察。其他板型的同原版、浏览器、真机、USB/iPhone
和无线功能均未执行。这一结果不转授 #188 的另一原版 DSI 读回或 #226 的 USB 完整验收。
本轮没有修改源码或常驻服务，无运行时回滚事项。

原始串口、帧和 ZIP 保持私有。公开摘要保留哈希、大小、物理范围和清理状态，
不含本机路径、会话标识、设备身份或认证信息。
