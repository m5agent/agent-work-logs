# StickS3 原版手表连续两次浅睡唤醒

同一原版 All day watch 0.3.8 在 Device Service 1.99.0 的同一 StickS3 会话中，通过两次 B 键唤醒和再次浅睡。两次唤醒均恢复 32,400 个非黑像素。两轮分别在第 20.817 和 20.795 秒采到 QMP `suspended` 及黑帧，前一次采样仍在运行且有画面。串口只有一次上电，第二次输入后至少观察 75.919 秒，未取得看门狗或软件复位证据。

本轮为虚拟设备验证。实体背光、耗电、外部慢钟及其他唤醒模式未执行。

- [复现步骤和边界](report.md)
- [运行记录](run.json)
- [逐帧状态与工件摘要](evidence/watch-two-gpio-wakes.summary.json)
- [上一轮单次唤醒](../../README.md)
