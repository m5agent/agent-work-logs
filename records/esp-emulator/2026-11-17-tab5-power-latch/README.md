# Tab5 ST7123 原版关机锁存

- 日期 2026-11-17
- 结果 `PASS`，虚拟设备验证
- 工作类型 `code_change`
- 问题来源 Arduventure 关机时反复输出请求，旧模型缺少终态
- 源码版本 `2a4edd56d1e7023e7fef30026f3760a4a083b24e`

原版 Arduventure 1.0.0 的电源图标长按使虚拟 P4 EN 拉低。会话保留关机帧和前后状态，显式重启返回原版标题帧。短按和图标外长按为负控。独立 CarPlay GT911 回归通过。

- [报告](report.md)
- [结构化记录](run.json)
- [脱敏证据](evidence/gateway-power-summary.json)
- [可复现测试](https://github.com/m5agent/m5stack-esp-emulator/blob/2a4edd56d1e7023e7fef30026f3760a4a083b24e/tests/firmware/tab5_st7123/run_power.py)

另一次并发回归确认了 EN 关机，DSI 报告丢帧且未捕获关机画面。本次覆盖指定 ST7123 运行配置。其他 Tab5 变体、物理供电与显示亮度、浏览器及常驻切换为 `NOT RUN`。

[冻结包独立复验](evidence/frozen-native-replay-summary.json)完成关机画面、EN、ZIP 和重启。

## 后续验证

- [Tab5 并发 DSI 取帧](followups/2026-11-17-tab5-dsi-readback/)
- [审核侧原版终端关机](followups/2026-11-17-tab5-review-terminal-power/)
