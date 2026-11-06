# 已结案全量实验包删除与最小证据保留

- 日期：`2026-11-06`
- 结果：`PASS`（主机文件系统清理与保留字节校验）。
- 来源：用户要求继续清理已结案实验数据；约27.4GiB未完成验证任务按先前选择保留。
- 源码仓库：[esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)，版本 `ea6a553b702c636b10692665c475341b178cb662`；产品源码未改。
- 环境：macOS arm64；文件系统、SHA、打开文件与Ninja产物规则核验。
- [前一轮固定记录](https://github.com/m5agent/agent-work-logs/tree/9f8dd7eaba6bd621b74416cb8b20047cccc17d6d/records/esp-emulator/2026-11-06-storage-and-clone-audit/)保留当时完整恢复PASS；本次追加当前可用性变化。

## 结论

本轮另净释放 **16,312,905,728 B（15.1926GiB）**。主项目目录实测由本轮开始时
**106.3374GiB降至91.1328GiB**；目录实测变化与逐项核算分开记录。

已删除24个已结案全量实验冷包，保留36,958条小证据路径及原索引/证明，新增保留目录
约0.3122GiB；所有选定路径完整SHA校验两轮通过。这24包完整原始材料现为
**NOT AVAILABLE**，摘要或SHA无法将其还原。独立历史归档不在此声明范围内。

另删除6,076个有明确生成规则的旧构建文件，64份生成配方留为约5.2MiB小包并实际完整恢复验证。
2,466份保护产物、19个源码仓库状态及8份Ninja生成图核对一致。

未完成验证任务、#188当前输入、已有源码改动、标准固件/运行环境未纳入删除名单。
后续只读检查发现该旧任务目前只有观察器，无实际guest执行；保留决定不等于正在运行。
五个probe仍依赖的独立work-image冷包约2.27GiB保留。

## 证据

- [报告](report.md)、[结构化记录](run.json)。
- [退役汇总](evidence/public-retirement-summary.json)、[24包身份与时间线](evidence/retirement-summary.json)。
- [选定小样本与哈希](evidence/retained-samples-summary.json)、[引用可用性核查](evidence/reference-update-plan.json)。
- [删除条件](evidence/deletion-conditions-summary.json)。
- [构建缓存清理](evidence/build-cache-summary.json)、[最终目录占用与源码保护](evidence/final-space-summary.json)。
- `patches/`、`code/`：不适用；无产品代码变更。

## 边界

guest、browser-WASM、物理硬件功能验证均为 `NOT RUN`；本轮不产生新的功能PASS。
私有原始路径、会话配置、日志或大包不随记录公开；仅发布脱敏计数、哈希及方法。
旧生成配方使用前需恢复小包或重新配置CMake，后续构建重新生成中间产物。
