# Nesso 触摸总线配置根因及修复

## 现象和实际原因

原 Launcher 3.0.0 BIN 在 `xTaskPriorityDisinherit` 中断言。实际 guest 指令记录显示，`loopTask` 已取得 Arduino SPI mutex，随后在 SPI 传输之前被输入任务抢占；`InputHandler` 调用真实 `getTouchRaw()`，因为触摸配置的 `bus_shared=true`，它执行显示面板的 `endTransaction()`，最终从错误任务释放 mutex。该证据排除了以增加 SPI/DMA 延时修复这一错误的解释。

Nesso LCD 使用 SPI MOSI21/SCLK20/CS17，触摸 FT6336 使用 I2C SDA10/SCL8。LCD 与 LoRa 的 SPI 共享配置仍须保留。修复范围仅为独立触摸的 `bus_shared=false`。布线依据见 [Arduino pinout](https://docs.arduino.cc/resources/pinouts/TPX00227-full-pinout.pdf) 和 [M5Stack Nesso 文档](https://docs.m5stack.com/en/core/Arduino_Nesso_N1)。

## 构建及执行

完整 Launcher 源码固定为 `4b06de691df15b0fe6a9f09f56d1d107bbf32b12`，M5Unified 0.2.24、M5GFX 0.2.31、PlatformIO 6.1.19、Arduino 3.3.9 与固定自定义 SDK。两个控制使用相同本地 gzip 生成流程，关闭外部 minifier 和源码格式化钩子。原发布构建所用 M5GFX 缓存版本不能唯一确定，因此不声称按位重建原 BIN。

另用最小双任务工程对固定 M5GFX 0.2.19 及当前 `28d47949bdc84f30881623476f555398e2194313` 作未修/修复对照。显示任务持有真实 SPI transaction 时，输入任务调用库的真实触摸 API。修复前真实 owner assert，修复后正确 owner release 持续递增并读回三个注入控制器坐标。完整操作和命令见 [复现说明](code/README.md)。

所有接受的运行使用 C6 runtime `e4c9bb8de6dba1395ab22712ec8dce58d4c2f701799598d289e1ffb9d5b4e7ec`，核对实际执行 PID 对应二进制 SHA，并比较应用分区执行前后字节。同会话 ZIP 在 stop 前获取，stop 使用保留历史模式，最终 PID、lease 和 mutable Flash 均释放。画面人工核对表明完整 Launcher 已进入菜单和设置页；probe 计数器持续推进。

## 证据与早期失败

[控制摘要](evidence/controls-summary.json)保留原 BIN 失败、三组源码控制、各固件与串口/帧/ZIP 哈希及输入。原指令因果摘要单列于 [original-mutex-trace-summary.json](evidence/original-mutex-trace-summary.json)。公开文件已去掉本机路径、端点、会话及唯一设备标识；它们是派生摘要而非 raw 日志。大型原始产物和第三方固件未随记录发布。

最初缺少 SPI 头文件依赖的探针未进入真实 mutex 路径，属于无效控制；一次修改未被编译的同名 PlatformIO 库也被相同 BIN 哈希识别，不算修复验证。接受的构建核对实际 compiler dependency 指向的版本，修复前后仅改变该触摸配置。

公开 runner 随后加强了最终 ZIP 完整串口的 fatal/重启检查，防止最后一次轮询与取证之间的异常漏判。两个 host unittest（含 15 个 helper 控制及 5 个实际 CLI mocked-I/O 终局负控）通过；四份已接受探针的完整串口经最终 oracle 重验通过，无新增 guest 运行。此 runner 哈希不追认成先前实际执行脚本的哈希。

## 兼容边界和回滚

本修复仅影响 Nesso 的独立触摸总线，不改变显示面板或 radio 的 SPI 共享。应用依然必须自行序列化并发显示操作。反向应用对应一行 patch 可回滚。物理硬件、RF、在线安装、当前 master 的完整 Launcher 构建未运行。原发布 BIN 保持 FAIL，不能继承重建版 PASS。Burner 未提交；模拟器主线/常驻整批发布另外验收。
