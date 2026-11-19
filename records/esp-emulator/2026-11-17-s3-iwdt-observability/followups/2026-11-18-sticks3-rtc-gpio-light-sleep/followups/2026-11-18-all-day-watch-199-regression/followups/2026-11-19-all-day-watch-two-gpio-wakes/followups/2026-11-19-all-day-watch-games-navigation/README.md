# All day watch 原版游戏菜单导航与再次唤醒

- 结果：`PASS`（原版离线 UI 导航与同会话睡眠/唤醒），`virtual-device validation`。
- 实测：B 唤醒后，A 打开原版游戏菜单；长按 B 2 秒返回逐字节相同的离线时钟画面，之后自然挂起，再一次 B 唤醒并再次自然挂起。
- 取证：帧、ROI、同会话输入和状态支持 UI 结论；实时 PC 仅作独立诊断，不能单独证明界面就绪。
- 修正：首轮 raw 的延迟字段实际在菜单操作后采集，不作为唤醒延迟；本次未见失败的来宾或观察器案例，历史失败仍保留。
- 限制：未进入或运行游戏，未联网校时；物理硬件、外部慢钟和浏览器未执行，未提交 Burner。
- 文件：[报告](report.md)、[执行](run.json)、[证据摘要](evidence/watch-games-navigation.summary.json)。
- 前序：[原版两次 GPIO 唤醒](../../report.md)。
