# StickC-Plus2 固件引导偏移校验

- 日期 `2026-11-16`
- 结果 `PASS`，限定原版镜像拒绝、审核状态和正常 ESP32 固件启动
- 工作类型 `issue`
- 来源 [#228](https://github.com/m5agent/m5stack-esp-emulator/issues/228)
- 源码 `12c01eab89c41794ecea4b5b4d3eadf63999feab` → `1cb1975be1828ed72fad22dce1098a9565f78f86`
- 环境 macOS arm64、独立 native Device Service、隔离审核进程及保存的描述快照

原版镜像把 ESP32 bootloader 放在 `0x0`。修复前导入及静态分析放行，ROM 从 `0x1000` 读出非法头并持续重试。修复后同一镜像在会话分配前被拒绝，审核任务为 `E_STATIC`，同时官方 UIFlow2 2.5.4 对照进入 Cloud 画面。证据来自 virtual-device validation。

- [报告](report.md)与[执行元数据](run.json)
- [旧版 ROM 复现](evidence/baseline-rom-summary.json)、[候选首次观测](evidence/candidate-first-observer-summary.json)、[候选复验](evidence/candidate-retest-summary.json)
- [复现入口](code/README.md) · [归档完整性](evidence/archive-integrity-summary.json) · [平台回归](evidence/platform-regression-summary.json)

测试未覆盖真机、浏览器执行和云端连接。补丁以源码提交身份保存。原始串口与 ZIP 留在私有证据目录。
