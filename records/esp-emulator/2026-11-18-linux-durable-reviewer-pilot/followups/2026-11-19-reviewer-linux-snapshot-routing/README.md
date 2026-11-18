# Reviewer 0.30.0 通过受管 Linux 复审原版 Core2 2048

- 日期 `2026-11-19`
- 结果 `PASS`，范围为保存快照路由、实际四向棋盘行为和审核历史读回
- 类型为原生 virtual-device validation
- 源码为 Reviewer `b9426a2d8a88338d95346ed9b93b0eaf0893cb9a`，Device Service 1.99.3 `2a7f979c0c7e67420d8b790a3cfdb692702abf05`
- 环境为 macOS 系统 Python 3.9.6、独立 Darwin Device Service 和无网卡 Linux ARM64 来宾

同一 Reviewer 的主就绪检查仍识别 Darwin，受管路由的就绪状态单独报告。使用普通保存快照复审 API 后，原版 2048 由 Linux 运行，上下左右各两次拖动均产生可证明的棋盘变化。运行期间读取的 SQLite 创建意图与实际 Linux 会话对应，Darwin 未创建会话。

关闭 Linux 新审核准入后重开同一 Reviewer 数据库，原有一条任务、17 条事件及证据目录精确一致。测试的替代目标不可达时只有 Linux 就绪检查返回 HTTP 503，恢复配置后返回 200。本轮未中断活跃审核，未执行 Reviewer 0.30.0 的 ADV 发音复审或常驻切换，未提交 Burner。

[执行报告](report.md) · [运行索引](run.json) · [脱敏证据摘要](evidence/reviewer-linux-snapshot-routing.summary.json) · [Linux 持久卷试点](../../README.md)
