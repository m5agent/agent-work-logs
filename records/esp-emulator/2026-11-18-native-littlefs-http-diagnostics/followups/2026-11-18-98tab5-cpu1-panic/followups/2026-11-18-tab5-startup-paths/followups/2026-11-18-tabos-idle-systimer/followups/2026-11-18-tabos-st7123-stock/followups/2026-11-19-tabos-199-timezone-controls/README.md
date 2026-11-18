# Tab5 ST7123 原版 M5TabOS 时区操作

在当前 Device Service 1.99.0 上，用同一 M5TabOS 0.9.1 原版运行 Tab5 ST7123。较长动作间隔的复测中，时区从 UTC−3:00 分别改到 UTC−2:30 和 UTC−3:30 并复原，随后进入地区网络选择页、选择不使用互联网，再返回时区页。8 次点按的压下和释放均获控制器确认。

较短间隔的早期轮次保留两次已确认但时区画面未更新的样本。快速交互稳定性继续开放，真机和 Burner 为 NOT RUN。

- [执行与限制](report.md)
- [运行记录](run.json)
- [画面区域与输入摘要](evidence/tabos-199-timezone.summary.json)
- [既有欢迎页回归](../../README.md)
