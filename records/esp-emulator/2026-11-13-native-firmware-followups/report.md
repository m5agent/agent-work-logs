# 执行与根因报告

本轮处理公开模拟器测试中的启动、显示、存储和输入问题。以同一原 BIN 的
串口、控制器寄存器、实际输入、帧和协议观察验证，过程中的先前 FAIL、
夹具或观察器错误另行保留；命令完成不被当作应用就绪。

## 已定位的原因

- Classic SPI 原先从寄存器读取固定面板 ID，错误板型也能通过探测；严格
  片选和实际 FIFO 响应恢复探测。硬件 CS 路由需要跟随 SPI 控制器，而非
  复用 GPIO 手动输出。RX DMA 缺失使真实 SD 初始化/读写失败；现由
  controller descriptor 和原 SD 命令模型完成，512 字节独立磁盘 oracle
  与 guest 结果一致。短链、owner、FIFO 上半区、双工覆盖和跨控制器 CS
  边界分别经真实 C 路径 ASan/UBSan 正反对照。
- 旧 UIFlow 每次 32 字节 Flash→PSRAM 读会重新打开 cache；原模型即使没有
  变化也失效整个映射并重复提交内存拓扑。现在只失效改变的 cache 数据，
  单次寄存器写合并拓扑更新，显式 flush、MMU 重映射和双核 PSRAM 保持。
  加载进度变快与硬件 CS 恢复画面使用独立控制；不声称物理缓存性能。
- Atom Matrix RX next/last 游标和 CCMP 路径修正后，原驱动完成网络事务。
  RMT 使用真实符号时钟和连续内存消费，LED 解码接受原 FastLED 等占空比
  的合法符号。真实厂测服务器返回 404 保留，不用 host fixture 改为成功。
- C6 QIO 地址/模式字节桥接原先造成 64 字节块读取错位；原 Bruce 的
  LittleFS 和主菜单恢复。SX1262 硬件/软件 SPI 共用真实寄存器状态。
  PHY 在无 host backend 时仍应存在，但不能生成 AP 接收包；BLE 专用
  AES 控制器独立执行 DMA 和加密，NIST 向量与原应用路径分别记录。
- StackChan I2C ISR 在拷贝最终 RX 数据前唤醒另一核心调用方，调用方
  返回并复用栈后仍遭 ISR 写入。原 BIN 和公开源码未修重建均失败；
  官方 SDK 补丁把通知移到 RX 拷贝后。两款只做此 SDK 改动的重建版
  各 360 秒、真实动画、触摸和 UART 舵机协议通过；未规避模拟器调度。
- 服务 QMP 错误清空连接后，原输入入口直接引用空连接。统一经过原有
  重连和错误处理，实际 guest 从欢迎页进入 launcher，失败请求不记 accepted。

## 复现与身份

每个 evidence JSON 自带 firmware、runtime、profile、原始证据摘要及
失败控制。下表绑定源码记录与复制到本归档的字节哈希；参考源码 README
包含独立 Device Service 或 checked-in regression 的命令。测试必须使用
隔离会话，先取 evidence ZIP，再停止并保留历史。

- [evidence/frame-orientation-summary.json](evidence/frame-orientation-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/docs/evidence/2026-11-13-native-frame-orientation/summary.json)，SHA-256 `51b79074aa292c2bc42a12aa8ca6a08387e9ed6f14273ab9b068f5401e12bdf5`。
- [evidence/p4-service-boundaries-summary.json](evidence/p4-service-boundaries-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/docs/evidence/2026-11-13-tab5-service-boundaries/summary.json)，SHA-256 `ce5b7a2e912a8d353ac13f2b65fa8d0b3a5b707a321a024da13edd1bd19e0cbb`。
- [evidence/atom-wifi-summary.json](evidence/atom-wifi-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/classic_factory/wifi-rx-summary.json)，SHA-256 `36fd4cbf6ba6abc93ef901dc3dba52fbc327d2c93a9168665205666ed2933a77`。
- [evidence/atom-rmt-led-summary.json](evidence/atom-rmt-led-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/classic_factory/rmt-led-summary.json)，SHA-256 `123e9ea8877cd63edd10d153a449581f4615863a1dd5007e88a46503f66e8190`。
- [evidence/core2-panel-summary.json](evidence/core2-panel-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/classic_panel_cs/evidence-summary.json)，SHA-256 `d1e3455864c6c844eba84d5e95eb6569b0295c12679485b6f114c773c04c411f`。
- [evidence/core2-sd-summary.json](evidence/core2-sd-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/classic_panel_cs/sd-evidence-2026-11-13.json)，SHA-256 `bad4a47075da7123e14286f1195121a9d15818d747f62ae8f04d12ad1b9d4186`。
- [evidence/core2-cache-summary.json](evidence/core2-cache-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/classic_cache_boot/summary.json)，SHA-256 `b8f9e034c4b0a290e6c41581354007cf55bb1b4466dddcf38abb5aa05a4dc087`。
- [evidence/c6-qio-summary.json](evidence/c6-qio-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/esp32c6_flash_qio/evidence-2026-11-13.json)，SHA-256 `65811d9cb63aefbd8cdcfd03d4e231140f526f1db236b5682ba588c23ce62c2d`。
- [evidence/c6-sx1262-summary.json](evidence/c6-sx1262-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/esp32c6_sx1262_spi/evidence-2026-11-13.json)，SHA-256 `1b850bc0c4572c1fa3d5a2071feb49018f133966296c4ec1b7a83405b6bda271`。
- [evidence/c6-isolated-phy-summary.json](evidence/c6-isolated-phy-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/esp32c6_radio_controllers/presence-evidence-2026-11-13.json)，SHA-256 `45b4e5664b42d477686fe9b97d2ad2b2b1a4de7a3f0d6be8abdb317c8e6399c5`。
- [evidence/c6-ble-aes-summary.json](evidence/c6-ble-aes-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/esp32c6_radio_controllers/aes-evidence-2026-11-13.json)，SHA-256 `0542799394cc49e4ebb47c07241b1d6a9a90a8c3a928f099042f4cff24e61072`。
- [evidence/stackchan-i2c-applications-summary.json](evidence/stackchan-i2c-applications-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/s3_i2c_lifetime/application-evidence-2026-11-13.json)，SHA-256 `799a97367e2ee1c8a4e8ba3839d7e37e395cfef41c9ecd6a3781e19297c6c6c1`。
- [evidence/input-reconnect-summary.json](evidence/input-reconnect-summary.json) — [固定源码](https://github.com/m5agent/m5stack-esp-emulator/blob/7d0ef3ea088c305cb6cd244eb8aabd67a3d0ffde/tests/firmware/service_input_reconnect/evidence-2026-11-13.json)，SHA-256 `5e3c6e4a4f732bae60546f867737800f8c65efc27ea53faca6ce23f0ddc1b1d0`。

## 兼容性、限制与回滚

这些结果只覆盖列明的固件、控制器与原生执行路径；browser-WASM 与真实
物理属性均独立验收。Tab5 最新镜像仍需闭源后端修复；C6 整应用后续失败
保持开放。StackChan 原 BIN 不会因新构建通过而被标为已修复。

源码修复按独立提交可回退；服务发布与回滚属于内部部署记录，不能由
本记录候选 PASS 推断已经替换常驻服务。本归档不包含凭据、设备唯一
身份、内部端点或本机路径；配置和完整串口、帧系列保留在受控原始存储。
