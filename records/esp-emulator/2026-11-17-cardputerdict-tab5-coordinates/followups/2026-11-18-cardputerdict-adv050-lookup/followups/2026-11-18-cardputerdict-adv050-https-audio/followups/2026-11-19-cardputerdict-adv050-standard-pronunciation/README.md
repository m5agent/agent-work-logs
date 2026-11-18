# CardputerDict ADV 0.5.0 标准审核发音回归

2026 年 11 月 19 日（UTC+08:00） · 虚拟设备验证 · **PASS**

Reviewer 0.27.0 对原版 ADV 保存快照返回 HTTP 202，随后在启动前报告发音类型不兼容。Reviewer 0.28.0 在固定原版、板卡和规范化 Flash 后执行真实输入。原版 ADV 允许场景达到 SIM_VERIFIED，缓存 10,605 字节 MP3，ZIP 和 API 均读到相同的 84,992 字节 PCM。拒绝场景正确阻断发音。初代 Cardputer 0.6.4 的同版兼容对照通过。

三次候选会话均导出并校验证据，随后释放 Flash、租约和临时网络资源。无 Burner 提交，常驻部署与实体设备未执行。

[报告](report.md) · [结构化记录](run.json) · [脱敏证据摘要](evidence/adv050-standard-pronunciation.summary.json)
