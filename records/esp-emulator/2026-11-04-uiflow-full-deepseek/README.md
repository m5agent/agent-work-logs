# UIFlow 全量复验：原生构建与来源基线里程碑

- 日期：`2026-11-04`（Asia/Shanghai）。
- 结果：**PARTIAL**。原生构建、公开来源复现及三项 CoreS3 canary 限定通过；完整功能验收进行中。
- 工作类型：`report`、`build_validation`、`firmware_validation`（本记录未新增产品代码）。
- 问题来源：用户要求先更新模拟器，再由 DeepSeek 执行 UIFlow API 与全部 Unit 复验；无独立公开 issue。
- 源码版本：[m5stack-esp-emulator @ b41eba70eb61f7ddc5c41e0b981341064f9d1d1f](https://github.com/m5agent/m5stack-esp-emulator/commit/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f)。
- 环境：macOS arm64、原生 Xtensa QEMU、固定 UIFlow API/Unit source inventory；功能执行计划使用可观察且保留历史的 Device Service 会话。物理硬件未执行。

## 结论

已从完整 canonical Unit 链重新构建原生 Xtensa runtime，产物 SHA-256 为 `0e16a9bcd86b588dae6b3e3b523dfb8610a9eca37c50c141cce5f2ceb4612068`。公开上游加 reviewed source-lock 与 board 层可重建其 canonical 基线，逐文件比较零差异。UI/API 源码基线和控制器资源身份已核对。原始驱动与控制器路径的三项 CoreS3 canary 已经主 agent 独立验收；Button 仅授予 constructor/GPIO input 路径，Relay 与 ENV III 授予已执行方法的限定 **virtual-device validation PASS**。完整 UIFlow API 与 Unit 功能结果尚未在本里程碑汇齐并独立验收，**不能写成全量 PASS 或目标完成**。

## 关键证据

- 构建：[native-build-summary.json](evidence/native-build-summary.json)，41 个 Unit 层逐层检查、fresh QEMU object build 与签名核验。
- 来源：[source-provenance-summary.json](evidence/source-provenance-summary.json)，47 个 source-lock native 层、10 个 board 层与显式中性上下文归一；10,443 项 canonical 文件/模式/链接完全一致。
- 产物/源码：[source-identity-summary.json](evidence/source-identity-summary.json)，固定源码及控制器资源 SHA；部署操作配置不公开。
- 服务功能执行：[cores3-canary-summary.json](evidence/cores3-canary-summary.json)，3 个独立保留会话、精确 runtime/firmware/probe/input/serial/frame/ZIP 与主 agent 独立验收；完整战役仍在进行。
- 日志/协议：构建原始日志仅保留 SHA；canary 摘要保留安全串口标记、输入值、控制器读回及全部 ZIP member SHA/大小，未复制原始 ZIP。

## 文件

- [report.md](report.md)：范围、验收分层、失败历史与后续条件。
- [run.json](run.json)：机器可读的限定里程碑。
- `evidence/`：审核用派生 summary 和[公开复现配方](evidence/public-recipe.md)，无 raw/private 运行数据。
- `patches/`：不适用；本记录复用固定源码中的补丁，没有新修复补丁。
- `code/`：不适用；固定项目源与配方足以复建，未重复复制源树。

## 未覆盖项

C6/P4/浏览器 WASM 不继承本次 Xtensa 构建；2 项 Unit DEFER（`mini-bps-v11`、`mini-pdm`）保留。官方 UIFlow API 可用性必须与 raw bus 探针、共享/别名驱动及候选固件分开判定；ButtonUnit 公共方法/callback 仍须补测，不能按 Unit ID 去重跳过。全量及跨主机分母仍待实际回执核对；物理 RF/电气/光学/声学/机械行为 `NOT RUN`。本条为已独立核对的阶段记录，不构成完整战役验收结论。
