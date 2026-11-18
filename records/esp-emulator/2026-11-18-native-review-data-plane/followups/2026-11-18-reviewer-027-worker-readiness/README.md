# Reviewer 0.27 候选就绪状态验证

2026-11-18，Reviewer 0.27.0 候选在实际 Device Service 1.99.0 隔离实例上通过 API 验收。Device 不可达或暂停接收新租约时，就绪检查返回 HTTP 503。Device 接收或恢复接收租约时返回 HTTP 200。旧健康检查继续可用，OpenAPI 回读为 0.27.0。

通过 API 就绪检查及候选单测后，已将同一版本推进 Reviewer 源码主分支。候选原版固件干跑和常驻部署为 `NOT RUN`。

[执行报告](report.md) · [运行记录](run.json) · [验证摘要](evidence/readiness.summary.json)
