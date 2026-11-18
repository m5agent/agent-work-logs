# Cardputer 原生 SPI SD 读响应与保存快照审核

- 日期为 2026-11-18，类型为原生运行时、Device Service 和 Reviewer 验证。
- Cardputer 与 Cardputer ADV 的原生控制器可回读接受的读命令及完整送出的 512 字节 SPI SD 响应块。
- 同一原版 CardputerDict ADV 0.5.0 的离线审核中，完整词库和缺正文卡均完成读响应，只有完整词库显示指定释义。无卡与旧运行时各有明确的取证结果。
- 原版 Cardputer ADV MP3 播放器的离线复跑完整送出 58 个块，并在同会话两段数字 PCM 中验证指定测试音。

[报告](report.md) · [运行清单](run.json) · [证据说明](evidence/README.md)
