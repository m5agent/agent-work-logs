# 原版 Tab5 的 GT911/ILI9881C DSI 命令和读回

本记录延续 [同原版 BMI270 和 ST7123 复验](../../README.md)。此处验证原版 UIFlow2 v2.5.4 的 GT911/ILI9881C 启动探测。精确 [Device Service 源码 1c2eb72d](https://github.com/m5agent/m5stack-esp-emulator/commit/1c2eb72d3b7e517e2ceb487c408708a5b800a8c8) 和 [esp-emu 1.1.0](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) 冻结后，原版 SHA-256 `94b6b43c02a95cfac1e7c70a6166ad669f308d0d16389c272de5ca7c2d45ef37`（16,121,856 字节）由普通 Device Service 导入为 16 MiB、SHA-256 `507f2aeeddfdd71357c019122cc76785b710ba24a4dc3adeb840d61c9ee8b1a7`。

| 冷启动会话 | 观察 |
| --- | --- |
| A1，无调试器，20.005 秒 | 实际后端报告 DSI 请求类型 DT `0x06` 由模拟器答零一次。原版 M5GFX 报告面板未识别一次。串口 406 字节，无软件复位或有效帧。 |
| A2，只读硬件断点，20.002 秒 | 在原版 SDK 入口 `0x4825bbc4` 读取到命令 `0x00` 和长度 1。返回原调用位置 `0x481c0010` 时，结果为 `ESP_OK`，本次请求的接收字节为 `00`。继续执行到原版面板未识别分支 `0x481a1d20`，移除断点并正常 detach。同样记录一次后端零回包和一次串口面板未识别，无软件复位或有效帧。 |

DT `0x06` 是原生后端记录的请求类型，`0x00` 是原固件传给 SDK 的读命令。原版中 SDK 错误字符串、应用指令和运行轨迹共同用于确认读取入口和失败分支。A2 未改变控制器寄存器、guest 内存、Flash、板型配置或读取返回值。两次均验证输出 ZIP CRC、清单各文件哈希、应用分区保留、可写 Flash 与租约释放、P4/C6 子进程及独立服务退出。

## 复现

1. 启动 [固定服务合约](https://github.com/m5agent/m5stack-esp-emulator/blob/1c2eb72d3b7e517e2ceb487c408708a5b800a8c8/docs/device-service.openapi.yaml) 实例，配置 `gt911-ili9881c` 与精确原生 GT911 Part，仅准入上面的 normalized SHA。冻结的运行时和 Part 哈希见 [有界证据](evidence/uiflow254-gt911-panel-read.summary.json)。
2. 标准上传并导入原 BIN，在两个新会话各创建 `tab5` / `runtime=qemu`。A1 无调试器。A2 通过会话提供的 GDB 端点在 `0x4825bbc4` 设硬件断点，读取 ABI 参数 `a1`、`a2`、`a3`，把当前 `ra` 作为同一次调用的返回断点。返回时读取 `a0` 和原 `a2` 缓冲区的第一个字节，继续至 `0x481a1d20` 验证原分支，再移除断点并 detach。
3. 保存两次串口、帧/API 观察和 `/evidence?include=manifest,serial,frames,logs,flash`。停止会话时使用 `?purge=0&retain_flash=0`，验证所属资源全部退出。

[上游固定 1.1.0 的 DSI 合约](https://github.com/espressif/esp-emulator/blob/34ba27a6e5a3da41743fc861b462cf2452f0ca28/docs/guides/HOST-INTERFACES.md) 说明面板模块接收输出命令和帧，固件发出的读取由模拟器以零应答。该复验把此边界绑定到原版 SDK 实际收到的字节以及随后执行的面板识别分支。真面板读回数据、原版 GT911 有效画面仍待验收。历史 ST7123 结果另有记录，本次没有重新运行。物理硬件、浏览器、联网、云端配对均为 **NOT RUN**。无固件或源码变更，无适用回滚，未提交 Burner。
