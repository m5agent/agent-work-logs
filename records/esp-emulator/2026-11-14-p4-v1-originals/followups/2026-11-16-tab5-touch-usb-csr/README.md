# Tab5 原版固件的触摸、USB 与 P4 启动诊断

- 日期 `2026-11-16`
- 整体结果 `PARTIAL`，#227 与 #226 保持开放
- 工作类型 `issue` 复验
- 运行时 `esp-emu 0.50.0` 和 `1.0.0`，P4 rev0 ROM、32 MiB PSRAM 与真实 ESP-Hosted C6 伴生实例
- Device Service 源码 `55e5763eac90a8166a3b0c522fd5291b99810517`，验证文档提交 `ca833e8475a7ea0975309620f860f72e4b6b7baa`

旧版运行时直接观测到 CarPlay-Tab5 触摸板型断言和 M5TabOS 0.9.1 USB DWC 核心 ID 断言。1.0.0 中，两份原版执行旧 P4 `csrr a4,0x346` 后进入异常向量。0.50.0 对照的同指令单步均到达 PC+4。所有结果来自 virtual-device validation。[#227 触摸探测](https://github.com/m5agent/m5stack-esp-emulator/issues/227) · [#226 USB 主机](https://github.com/m5agent/m5stack-esp-emulator/issues/226)

九个 guest 会话的证据、停止和清理已核对。应用画面因缺少匹配的 ELF 未采到，触摸输入、USB 主机枚举、网络数据面、真机和浏览器 WASM 均为 `NOT RUN`。

[11 月 14 日原记录](../../README.md) · [详细报告](report.md) · [结构化结果](run.json) · [逐轮证据](evidence/runtime-summary.redacted.json) · [完整性校验](evidence/archive-integrity-summary.json)
