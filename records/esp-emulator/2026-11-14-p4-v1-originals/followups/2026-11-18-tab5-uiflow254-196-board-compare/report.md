# Tab5 UIFlow2 原版的面板识别输入与输出

使用 Device Service 1.96.0 源码 `a7dbd9808a09bc507b657995dba079b8075badcf` 和 Espressif esp-emu 1.1.0 原生运行时 `633a35f993300a765634ed78a2dbcfd5ffcd5c3f2f354a2dddabeb6108240828`。同一份官方 Tab5 UIFlow2 2.5.4 原版完整输入 16,121,856 字节，SHA-256 `94b6b43c02a95cfac1e7c70a6166ad669f308d0d16389c272de5ca7c2d45ef37`，规范化 SHA-256 `507f2aeeddfdd71357c019122cc76785b710ba24a4dc3adeb840d61c9ee8b1a7`。三组都在自有隔离服务执行，P4 和 C6 仅使用本地 Hosted 桥接。运行后逐字节核对实际虚拟 Flash 中的原版应用分区。[固定源码](https://github.com/m5agent/m5stack-esp-emulator/tree/a7dbd9808a09bc507b657995dba079b8075badcf)

| 同原版执行 | 观察 | 判定 |
| --- | --- | --- |
| GT911／ILI9881C，无调试器 | 约 20 秒内只观察到一次 ROM 启动、零软件复位、零完整帧，以及一次 `M5Tab5 display panel was not detected`。406 字节串口与 Device Service 1.92.0 的同固件普通冷启动完全一致。 | **FAIL**，原版画面未就绪。 |
| ST7123，无调试器 | 11 个完整帧样本中 10 个非黑。主页的稳定区域匹配既有原版回执，在面板坐标 `(83,308)` 点按后收到两次触摸报告和两次确认。随后 720×1280 帧的扫描表区域匹配既有原版 I²C Scan 页面。 | **PASS**，离线主页和实际触摸后页面。 |
| GT911／ILI9881C，单独的只读断点会话 | 读回面板 ID 三个字节和原版应用的第一条比较，随后原流程进入未识别面板分支。调试器正常脱离，会话继续至正常观测窗口结束。 | **PASS**，观测识别条件。画面仍为 **FAIL**。 |

在 `0x4825bbc4` 观察 `0x00` 读请求长度 1，返回 `ESP_OK` 且缓冲区为 `00`。原版调用者继续执行 `0x01` 和 `0x02` 两个单字节读取，在 `0x481a1da8` 的第一条条件分支前，三个读回值为 `00 00 00`，实时寄存器中第一字节期望值为 `98`。原版指令在第一条件满足时才把第二字节和 `81` 比较。本轮实际执行了第一条件失败的分支，再到 `0x481a1d20` 的未识别面板路径。指令显示读取前还有一条携带三个字节的 `0xFF` 命令，未读取这条命令的实际载荷。[有界寄存器和会话回执](evidence/uiflow254-tab5-board-id.summary.json)

当前上游 1.1.0 发布和固定 Host 接口文档均明确底层对 DSI 读填零。目前 I²C 触摸 Part 可以报告触摸，标准 MIPI DSI 接口能观察命令和视频帧，已发布的接口没有可用于此判定的同步面板读取回包。下一步需要让板型专用 ILI9881C 响应沿 ESP32-P4 DSI 读通路返回，从而用同一原版验证读回、识别、自然画面和 GT911 触摸。至少应先用受控 SDK 读请求验证非零、错误值及无面板响应，再执行原版闭环。[Espressif 1.1.0](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) · [固定 Host 接口文档](https://github.com/espressif/esp-emulator/blob/34ba27a6e5a3da41743fc861b462cf2452f0ca28/docs/guides/HOST-INTERFACES.md) · [M5Stack Tab5 硬件文档](https://docs.m5stack.com/en/core/Tab5?id=schematics)

## 复现

1. 用上面的固定运行时、各板型原生 Part 和同一原版 BIN。以独立 Device Service `POST /api/v1/artifacts`、`POST /api/v1/firmware/import`、`POST /api/v1/sessions` 创建原生会话。每轮重新冷启动。
2. GT911／ILI9881C 用标准帧端点观察 20 秒并读串口。ST7123 进入主页后用标准 input 端点点按 `(83,308)`，分别核对控制器报告和 I²C Scan 页面稳定区域。
3. 在另一个同固件 GT911 会话，对 SDK 读取函数与其原版调用者设置硬件断点。只读入参、返回、目标缓冲区和第一比较寄存器，捕获错误分支后脱离。另保留无调试器的普通冷启动对照。
4. 停止前保存标准证据 ZIP 检查清单和 CRC。用 `purge=0` 停止会话，核对 Flash 释放、零活跃租约、所属 P4/C6 进程和独立服务退出。原始图像、串口和调试转录仅保留于执行现场。

截至 2026-11-18，该问题仍开放。云端配对、物理硬件、浏览器和非零面板回复正向路径为 **NOT RUN**。未提交 Burner。[#188](https://github.com/m5agent/m5stack-esp-emulator/issues/188)
