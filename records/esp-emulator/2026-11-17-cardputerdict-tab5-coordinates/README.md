# CardputerDict 原版查词与 Tab5 原生触摸复验

日期 2026-11-17。结果 PARTIAL，工作类型为运行验证与报告。桌面主机使用两个独立虚拟设备运行时。具体构建身份、固件和证据哈希见结构化记录。

普通 Cardputer 的 CardputerDict 0.6.4 从 FAT32 SD 加载自编词库并打开指定词义。Tab5 的审核器按同一会话原生帧计算触点，CarPlay 来宾经 GT911 确认了接触与释放。两个 saved_snapshot 审核仍保留 SIM_PARTIAL。 [CardputerDict 发布说明](https://github.com/RadioDisney/CardputerDict/releases/tag/v0.6.4) · [Tab5 板型问题 #227](https://github.com/m5agent/m5stack-esp-emulator/issues/227)

- [执行报告和复现方法](report.md)
- [机器可读运行记录](run.json)
- [CardputerDict 证据摘要](evidence/cardputerdict-summary.json)
- [Tab5 坐标证据摘要](evidence/tab5-coordinate-summary.json)

归档提供证据哈希与可重建测试数据说明。原版固件只有身份记录，公开附件不分发固件、可写 Flash 或原始 ZIP。自编测试词条采用 CC0。
