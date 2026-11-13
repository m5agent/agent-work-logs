# Nesso N1 独立触摸总线的 mutex 修复

- 日期：`2026-11-13`
- 结果：`PASS`，限定源码修复前后对照；原发布 BIN 仍为 `FAIL`。
- 工作类型：`code_change / issue`
- 问题来源：[ESP Emulator #216](https://github.com/m5agent/m5stack-esp-emulator/issues/216)
- 源码版本：M5GFX `28d47949bdc84f30881623476f555398e2194313`；完整 Launcher 源码及 SDK 固定值见 [source-pins.json](code/source-pins.json)。
- 环境：Nesso N1 原生 C6 Device Service，`virtual-device validation`；未使用物理硬件。

Nesso 触摸使用独立 I2C，总线共享配置却使输入任务结束显示任务持有的 SPI transaction，触发 FreeRTOS mutex owner 断言。补丁仅将触摸 `bus_shared` 改为 false，LCD 的共享 SPI 配置保留。完整 Launcher 源码对照和当前 M5GFX 的最小并发复现均通过。

## 关键证据

- 原版 Launcher 3.0.0 的实际指令轨迹定位到错误任务释放 mutex，原 BIN 未修改。
- 完整 Launcher：未修版约 1.8 秒断言；修正版超过 155 秒，菜单选择、触摸、返回及设置页正常。
- 固定当前 M5GFX：未修版约 1.47 秒断言；修正版超过 155 秒，586 次正确 owner release，三个真实控制器触摸坐标。
- 运行时 SHA-256：`e4c9bb8de6dba1395ab22712ec8dce58d4c2f701799598d289e1ffb9d5b4e7ec`。固件、串口、帧及 ZIP 的 SHA 和清场结果见 [控制摘要](evidence/controls-summary.json)。

## 文件

- [report.md](report.md)：根因、构建、复现和边界。
- [run.json](run.json)：分层状态及文件身份。
- [evidence/controls-summary.json](evidence/controls-summary.json)：经过白名单提取的控制摘要。
- [原 BIN 指令摘要](evidence/original-mutex-trace-summary.json)：未经重建 ELF 地址推断的实际执行轨迹。
- [code/README.md](code/README.md)：可复现工程、构建与专用 Device Service 操作。
- [当前 M5GFX 补丁](code/m5gfx-master.patch)、[M5GFX 0.2.31 补丁](code/m5gfx-0.2.31.patch)：各一行修复。

## 未覆盖项

物理硬件、RF、在线安装及当前 M5GFX 的完整 Launcher 构建为 `NOT RUN`。当前 master 用最小并发工程执行相同库和 Arduino SPI 路径。本修复不保证任意并发显示操作安全，也不修复旧 BIN；未提交 Burner。
