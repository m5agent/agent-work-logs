# ESP Emulator 社区固件问题修复与复测

- 日期：`2026-11-13`
- 结果：`PARTIAL`
- 工作类型：`issue / code_change / virtual-device validation`
- 问题来源：[公开 issues #216–#224](https://github.com/m5agent/m5stack-esp-emulator/issues)
- 源码快照：[`98287067eaf558576d1120f213d676630d66c2bd`](https://github.com/m5agent/m5stack-esp-emulator/commit/98287067eaf558576d1120f213d676630d66c2bd)；原始运行各自的源码和产物身份见证据。
- 环境：固定源码构建的原生 QEMU、独立 Device Service 会话；原版公开 BIN 与诊断固件分别留证。

## 结论

#217、#218、#219、#220、#224 完成下表所述的限定修复或验证。#216、#221、#222、#223 仍开放。首次完整原生矩阵为 66 PASS / 2 FAIL，修正音频用例的就绪观察后最终运行时七例通过；这不是重新执行全部 68 例。最终源码已固定，平台套件结果待补，批次保持 `PARTIAL`。

| Issue | 已建立的结论 | 边界 |
| --- | --- | --- |
| #217 | 跨 vCPU TLB flush 修复；原 PaperColor 300.74 秒无宿主崩溃 | 仍有 1 次 guest 断言、2 次重启标记，应用 PARTIAL |
| #218 | QMP 主动关机判定、末帧与正常清理通过 | 关机/白屏不是应用就绪 |
| #219 | 原版 AtomS3 Snake/UserDemo 显示、120 秒运行与限定输入响应 | GC9107 变体；帧变化不等于四方向游戏语义 |
| #220 | 原 PaperColor MSC EP0 描述符、配置和 GET_MAX_LUN 通过 | 不是 CDC、块存储 I/O 或完整工厂应用 PASS |
| #224 | Classic eFuse 字节序/CRC、API 身份和重启恢复通过 | Core2/C6 明示未供给身份，不改上传 NVS、不宣称应用就绪 |
| #216、#223 | 部分修复/可执行诊断已建立 | 两项仍开放 |
| #221 | 最终服务两轮 Atom Lite 冷启 121.90/121.85 秒及按键→RMT 通过 | Matrix 仍有 Wi-Fi watchdog、灯阵无输出；旧冷启失败保留 |
| #222 | UIFlow 启动 Logo、HamRadio 配置检查已观察 | 均未达到应用就绪；板型/时间片控制未构成修复 |

## 关键证据

- 构建或运行：[首次整合摘要](evidence/integration-summary.json)，原生运行时 SHA 固定，失败输入观察保留。
- 最终运行时：[显示、USB、关机与 atomic 复测](evidence/final-runtime-summary.json)；[首轮 68 例结果](evidence/native-matrix-first-summary.json)与[音频观察修正及七例复测](evidence/audio-readiness-summary.json)分别保留。
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
[待补字段](evidence/pending-final-results-summary.json)保留尚未完成的平台套件结果；未执行的新一轮完整 68 例矩阵明确为 `NOT RUN`。所有已知应用失败均保持开放。
