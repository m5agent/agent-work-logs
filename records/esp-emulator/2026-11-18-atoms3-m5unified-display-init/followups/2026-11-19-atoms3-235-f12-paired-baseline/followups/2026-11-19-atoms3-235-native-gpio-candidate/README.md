# AtomS3 #235 原版显示初始化候选验证

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `PASS`，覆盖原生模拟器的三款原版和同机型对照
- 问题来源 [Issue #235](https://github.com/m5agent/m5stack-esp-emulator/issues/235)
- 环境 隔离 Device Service 1.99.2、AtomS3、签名后的原生 Xtensa QEMU

原版 Spirit Level、Motion Face 和 Pocket Clock 在默认机型均于约 2.04–2.07 秒出完整 128×128 非黑帧。同一原版与 Flash 摘要保持一致。五轮记录的首条面板命令均为 `0x04`，早于首条 GP-SPI 转发。官方 UIFlow2 终帧与基线逐字节相同，另以显式 GC9107 覆盖独立复验 Spirit Level。

Spirit Level 的 ±0.75g 输入在原应用上显示正负约 36.9°，并有 MPU6886 寄存器读回。Motion Face 有相应的寄存器读回和不同画面，Pocket Clock 显示离线配置界面。五轮均释放可写 Flash、子进程退出并归零租约。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏证据](evidence/atoms3-235-native-candidate.summary.json) · [三份原版与官方固件基线](../../README.md)

详细 RDDID 位流、实体板、真实 Wi-Fi 和浏览器未执行。候选未部署到常驻服务，Burner 未提交。
