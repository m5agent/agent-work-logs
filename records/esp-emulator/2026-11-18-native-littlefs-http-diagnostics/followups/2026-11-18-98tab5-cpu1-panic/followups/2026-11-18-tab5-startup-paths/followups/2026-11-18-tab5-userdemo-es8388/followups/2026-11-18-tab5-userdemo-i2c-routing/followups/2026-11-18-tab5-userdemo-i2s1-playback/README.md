# Tab5 UserDemo 原版的仪表盘、触控和 I²S1 播放

2026-11-18 · Tab5 GT911/ILI9881C · virtual-device validation

未改动的 UserDemo V0.4 在隔离候选 Part 上显示完整仪表盘。两次真实触控依次打开 Music Test、按下 PLAY MUSIC。随后采到 48 kHz 双声道 16 位 PCM。保持同一按钮空闲的对照在启动声之后只产生零值样本。

候选结果为 **PASS（隔离虚拟路径）**。候选未进入生产准入或常驻服务，GT911 CarPlay/UIFlow2 回归、浏览器和实体硬件未运行。

[执行与证据](report.md) · [机器记录](run.json) · [有界验证摘要](evidence/userdemo-codec-i2s1-playback.summary.json) · [上一次 I²C 路由对照](../../README.md)
