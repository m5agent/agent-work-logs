# Tab5 停机回写未确认时拒绝复位

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `PASS`，模拟器拒绝重启未经回写确认的 Flash
- 工作类型 `validation`
- 环境 macOS ARM64，原生 Tab5 ST7123，Device Service 1.99.1

M5TabOS 0.9.1 原版已正常进入离线桌面。测试只中断本次会话持有、启用 Flash 回写的 P4 进程，随后调用标准 reset API。服务返回 HTTP 409 `tab5_flash_save_failed`。同一会话进入失败终态，P4 和 C6 均未重新启动。原会话证据可读回，两种进程均已退出，租约归零，可写 Flash 已释放。

[正常复位和停机保留验证](../../README.md) · [执行报告](report.md) · [结构化记录](run.json) · [脱敏后的证据摘要](evidence/p4-reset-crash-fence-summary.json)

本次覆盖原版固件的原生离线路径。真机断电、浏览器、联网和其他固件为 `NOT RUN`。Burner 未提交。
