# Spirit Level 保存快照复验

历史保存的 Spirit Level 审核在应用就绪阶段返回 HTTP 408，原因 `E_NO_FRAME`，并留下 125 字节的回退帧。本次在独立状态中以同一原版和同一份审核描述构造保存快照，调用标准重试路由并保持默认审核选项。HTTP 202 接收重试后，Reviewer 0.29.0 在系统 Python 3.9.6 上调用 Device Service 1.99.2，创建默认 `m5atoms3-st7735` 原生访客。Device Service 源码固定在 `f12b15fb`，启动的 QEMU 为[前序对照验证](../../README.md)中同一签名产物。此复验没有代码改动或回滚操作。

复现实验可沿保存快照审核路径调用 `POST /api/reviews/{id}/retry`，在专用 Device Service 环境保留 `POST /api/v1/sessions/{id}/wait` 的响应、Reviewer 的应用就绪和观察证据。使用原版 SHA-256、规范化 Flash SHA-256、对应 ROM 和 QEMU SHA-256 校验运行身份，再在停止前保存证据 ZIP。HTTP 路由的路径参数由本次创建的审核和会话记录提供。

新的就绪检查实际返回 HTTP 200，且 `initial_ready=true`；就绪前未用输入解锁画面。实时截图和 ZIP 的同一 998 字节 PNG 一致，画面尺寸 128×128，16,384 个非黑像素、5 色。持续观察取样 13 次，实际 60.009 秒。独立回读核验 ZIP CRC 和 8 项成员哈希，将就绪响应、观察记录、审核报告和 ZIP 清单绑定到同一会话。ZIP 内 8 MiB Flash 的 `[0x10000, 0x94e40)` 区间与原版对应字节一致。

本次终态是 `manual_review / SIM_PARTIAL / E_INTERACTION_CLAIM_PARTIAL`。审核描述由通用解析器推断为 `touch_hold_center`，分别保留两段描述时均出现这项推断，清空描述时该项消失。触摸操作状态为 `NOT RUN`；这里的结果证明了应用就绪和画面观察，实际描述交互仍待验收。原版倾斜行为和显示改动的原生对照以[前序独立验收](../../README.md)为准。

专用服务和访客退出，活动租约为零，停止历史可读，Flash 已释放。实机、浏览器、访客网络和常驻路由未运行。Burner 未提交。公开内容保留摘要、证据长度与 SHA-256，省略作者文字、原始 ZIP、日志、路径和独有标识。 [脱敏证据摘要](evidence/atoms3-spirit-reviewer-029.summary.json)
