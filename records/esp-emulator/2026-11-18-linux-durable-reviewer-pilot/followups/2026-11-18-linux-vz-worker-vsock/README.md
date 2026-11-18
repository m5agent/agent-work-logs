# 无虚拟网卡的 Linux Worker 就绪通道

- 日期 `2026-11-18`
- 结果 `PASS`，范围为独立实验中宿主访问 Linux Device Service 的单个只读接口
- 工作类型 `infra_baseline`
- 源码 `ff8a7dc005ad38aa8e40b778a0467a5ee1d5ebec`，执行端代码与 `a729e24b1e4724b783ab2d59eec689cfdfeb24b3` 一致

宿主环回通过 Virtio VSOCK 请求无网卡 Linux 来宾中的真实 Device Service。缺少凭证或凭证错误均返回 HTTP 401，正确凭证返回 200 和可接收租约的 Linux Worker 状态。另一条 API 路由返回 404，写入方法请求返回 501。结束后服务、连接和虚拟机均退出，活动租约为零。

固件执行、可信 HTTPS 发音及生产审核路由切换均未执行。没有 Burner 提交。

[执行报告](report.md) · [机器可读记录](run.json) · [有界证据](evidence/worker-vsock.summary.json)
