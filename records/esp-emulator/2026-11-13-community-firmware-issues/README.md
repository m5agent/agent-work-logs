# ESP Emulator 社区固件问题修复与复测

- 日期：`2026-11-13`
- 结果：`PARTIAL`
- 工作类型：`issue / code_change / virtual-device validation`
- 问题来源：[公开 issues #216–#224](https://github.com/m5agent/m5stack-esp-emulator/issues)
- 源码快照：[`cf232dbcc93adacab224d6d2fce44c1f55ed0894`](https://github.com/m5agent/m5stack-esp-emulator/commit/cf232dbcc93adacab224d6d2fce44c1f55ed0894)；最终整合提交待补。
- 环境：固定源码构建的原生 QEMU、独立 Device Service 会话；原版公开 BIN 与诊断固件分别留证。

## 结论

#217、#218、#219、#220、#224 完成下表所述的限定修复或验证。#216 的 AES 等待已修，但整项仍开放；#223 已定位 I2C 接收缓冲区生命周期竞态，原版固件仍失败。#221、#222 和最终 68 项原生矩阵尚待补齐，不能据此宣布全部社区固件可用。

| Issue | 已建立的结论 | 边界 |
| --- | --- | --- |
| #217 | 跨 vCPU TLB flush 修复；原 PaperColor 300.74 秒无宿主崩溃 | 仍有 1 次 guest 断言、2 次重启标记，应用 PARTIAL |
| #218 | QMP 主动关机判定、末帧与正常清理通过 | 关机/白屏不是应用就绪 |
| #219 | 原版 AtomS3 Snake/UserDemo 显示、120 秒运行与限定输入响应 | GC9107 变体；帧变化不等于四方向游戏语义 |
| #220 | 原 PaperColor MSC EP0 描述符、配置和 GET_MAX_LUN 通过 | 不是 CDC、块存储 I/O 或完整工厂应用 PASS |
| #224 | Classic eFuse 字节序/CRC、API 身份和重启恢复通过 | Core2/C6 明示未供给身份，不改上传 NVS、不宣称应用就绪 |
| #216、#223 | 部分修复/可执行诊断已建立 | 两项仍开放 |
| #221、#222 | 最终修复/对照待补 | 不写入提前关闭结论 |

## 关键证据

- 构建或运行：[首次整合摘要](evidence/integration-summary.json)，原生运行时 SHA 固定，失败输入观察保留。
- 产物或部署：[证据来源与摘要哈希](evidence/provenance-summary.json)；本记录未发布固件、运行时二进制或原始 ZIP。
- 实机或服务执行：仅 **virtual-device validation**；物理硬件 `NOT RUN`。
- 日志、协议与行为：逐 issue 的原版固件 SHA、运行时 SHA、串口/帧/协议与清理摘要见 [完整报告](report.md)。

## 文件

- [report.md](report.md)：根因、修复、复现入口、失败控制与边界。
- [run.json](run.json)：机器可读状态与证据索引。
- [evidence/](evidence/)：经审查的 curated summaries，均不是原始数据。
- `patches/`、`code/`：不适用；修复和可重建测试工程通过报告中的固定源码链接提供，避免复制第三方 SDK 或构建产物。

## 未覆盖项与待补

物理硬件、RF、电气、光学、机械和浏览器 WASM 均 `NOT RUN`。没有提交 Burner。
[待补字段](evidence/pending-final-results-summary.json)明确保留最终源码提交、平台套件、68 项原生矩阵及 #221/#222 的状态；填写前批次保持 `PARTIAL`。
