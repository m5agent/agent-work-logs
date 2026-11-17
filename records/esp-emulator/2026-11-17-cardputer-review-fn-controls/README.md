# Cardputer Fn 单击及三键组合审核复验

- 日期 `2026-11-17`
- 结果 `PARTIAL`
- 工作类型 `code_change`
- 问题来源为固件审查语义输入待办。
- 源码为固件审核服务 `fa90d9a361a3b27e4d9eb02e76d7245e9c485e73` 与 Device Service `4160e5d27732742052e2246bffb773a718373ca6`。
- 环境为 macOS arm64 原生 Xtensa 虚拟设备，使用会话独占的 FAT32 测试词库。

本地审核从说明中识别 Fn 单击、带中文名的实体退格键和带 Shift 的三键组合。CardputerDict 0.6.4 原版分别在初代 Cardputer 与 Cardputer ADV 上完成缓存重载和强制重建的 SPI 对照。

| 操作 | CMD17 读命令 | CMD24 写命令 |
| --- | ---: | ---: |
| Fn+R | 69 | 0 |
| Fn+Shift+R | 110 | 11 |
| Fn+R | 69 | 0 |

Cardputer ADV 随后显示所输入的 `qu`。无输入期间画面保持相同，Fn+Backspace 后恢复到已确认的空查询画面。

旧版和新版用同一份 CardputerDict ADV 原始 BIN 和保存说明复审。旧版遗漏 Fn+Shift+R，新版发出包含三个键的单次输入请求。原版整体仍待复核。普通审核在组合键到达前已打开 Wi-Fi 设置，强制重建另在同原版的搜索页会话验收。联网、硬件和 Burner 提交均未执行。

[报告](report.md) · [结构化记录](run.json) · [证据摘要](evidence/execution-summary.json)
