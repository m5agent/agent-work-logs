# PaperColor 原厂固件在无宿主 USB 通信时的互斥锁断言

保持原 BIN、运行时和离线条件。独立的普通冷启动未发送宿主 USB 通信，仍出现 `xTaskPriorityDisinherit` 和重启。独立只读任务观察确认触发断言时，当前任务与另一核上运行的锁持有者不同。

互斥锁的完整取得和释放顺序、修复及真机验证仍开放。三轮均保留证据、释放租约和可写 Flash。Burner 未提交。

- [方法与边界](report.md)
- [精确身份和摘要](evidence/papercolor-no-host-usb-mutex.summary.json)
- [执行记录](run.json)
- [上一轮原版 MSC 对照](../../README.md)
