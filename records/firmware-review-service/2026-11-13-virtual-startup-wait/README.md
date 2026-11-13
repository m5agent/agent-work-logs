# 固件审核等待虚拟设备启动

- 日期 `2026-11-13`
- 结果 `PASS`（审核启动流程），`PARTIAL`（两份固件的功能覆盖）
- 工作类型 `code_change`
- 环境为 Cardputer ADV 和 StickC Plus2 原生虚拟设备，以及保存快照 dry-run。
- 基础与修复版本、执行记录及补丁见 [run.json](run.json)。

审核服务现在等待虚拟闪存准备与模拟器进入 `running`，随后开始应用就绪检查。两份原固件均从空缓存完成虚拟烧录并进入运行。S1-ADV 到达首次配置界面并完成 60 秒观察。JIGGLER 的虚拟闪存准备超过旧版 12 秒窗口，随后在虚拟设备上复现 CPU1 看门狗 panic，审核已识别该崩溃。

- [诊断、复测和验证边界](report.md)
- [虚拟设备证据摘要](evidence/virtual-startup-summary.json)
- [审核器补丁](patches/0001-wait-for-virtual-startup.patch)
