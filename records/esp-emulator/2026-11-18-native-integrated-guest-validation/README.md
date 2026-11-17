# StickS3、Dial、NC1020 与 Core2 原生联合复验

- 日期 `2026-11-18`
- 结果 `PARTIAL`，限本文列出的虚拟设备路径
- 工作类型 `report`，四条设备路径的联合验证
- 源码 `m5stack-esp-emulator@bd1dca3c74f8b9c2654e1ba3590e1f282d2071b0`
- 环境为独立原生 Device Service，Xtensa QEMU SHA-256 `44d5b221e506c6b85dcc5d46d9d97a202eb6eca0a5713108a95f35676aed50f5`

StickS3 原版首次配置并在同一会话的两次重置后重新取得 DHCP、ARP。Dial 原版六项播放与音量控制通过，十次旋钮选曲中一处快反转漏选，官方固件的画面正控通过。NC1020 原版冷导入的 206/206 ROM bank 与 512 KiB NOR 都与本轮合成载荷匹配，G0 存档通过，画面未达到视觉验收。Core2 的 abort 和 watchdog 受控固件均验证了匹配 ELF 的 FreeRTOS 任务元数据、归档与重启回读。

[报告](report.md) · [结构化结果](run.json) · [测试与证据索引](evidence/README.md)

[后续复验](followups/2026-11-18-native-guest-followup/)记录 Flash 容量、S3 转储、StickS3 新会话及原版画面与输入的剩余边界。
