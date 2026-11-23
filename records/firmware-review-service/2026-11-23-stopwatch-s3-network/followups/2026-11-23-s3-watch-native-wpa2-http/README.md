# S3-watch 原版 WPA2、HTTP 与组合兼容性边界

- 日期：`2026-11-23`
- 结果：`PARTIAL`；S3-watch 限定正控与错口令控制通过，组合 runtime 提升仍 `BLOCKED`。
- 工作类型：`code_change`
- 问题来源：[此前网络审查复验](../../)
- 源码身份：本地封存 `073104c072ebfab24ed010216a6ea24e0ba4ea4e`，未推送公开项目源码。
- 环境：macOS arm64 隔离原生 Device Service、`m5sticks3`、Unix socketpair，宿主 IP 后端为零。

## 结论

相同 8 MiB S3-watch 原版经真实 B 长按关/开后，目标 WPA2 握手、受保护 TX/RX、DHCP 与固定 `GET /api/state` 均有同会话证据；维护版 runner 重复通过。错口令没有达到 ready、DHCP 或 HTTP，预期拒绝检查通过。原版未校时的合法占位不再被 HTTP oracle 错拒，早期 FAIL 保留。

组合 runtime 的旧 StopWatch 门户完成 HTTP 后未完成 STA，而旧二进制的同配置基线通过。打开现成 trace 后两版均通过，原因仍未定位，不能提升为组合主线或生产部署。

## 关键证据

- [脱敏聚合摘要](evidence/s3-watch-native-wpa2.summary.json)：正控、错口令、维护 runner、初始/B 键状态、早期失败、组合对照、测试和清理。
- [完整报告](report.md)
- [结构化清单](run.json)

记录只包含有界摘要与哈希，没有读取或发布敏感原代码、凭据、原始抓包、帧系列和 ZIP 字节。未验证 Linux、浏览器、常驻部署、物理 RF/安全或外网，未提交 Burner；Reviewer 自动输入编排仍是独立工作。
