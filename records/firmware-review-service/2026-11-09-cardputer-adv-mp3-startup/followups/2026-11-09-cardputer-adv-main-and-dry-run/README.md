# Cardputer ADV MP3 Player 主线交付与 dry-run

- 日期 `2026-11-09`
- 结果 `PARTIAL`，原生 dry-run 播放通过，真机与浏览器挂卡播放未测
- 工作类型 `code_change`
- 源码基线 `80d1879a014a55bc598fbc1474445c1f6773ff34`
- 待合并修复 `340d80cf2e54bbe867f5dbade422ac0907251607`
- 环境为 Cardputer ADV 原生 Xtensa QEMU 虚拟设备验证
- 固件为原版 v1.0.0。审查模式为 dry-run，提交选项关闭。[上游版本](https://github.com/TurbulentGoat/cardputer-adv-mp3-player/releases/tag/v1.0.0)

## 结论

本地与远端主线均为 `340d80cf2e54bbe867f5dbade422ac0907251607`，两项 CI job 已通过。原版固件的保存快照审核为 `done / SIM_VERIFIED`，报告为 `NOT SUBMITTED`。同一会话在回车后读到曲目扇区，显示播放界面，并输出匹配的 524 Hz 虚拟扬声器 PCM。[精确提交 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42548926018)先前独立运行的功能证据保留在原报告。[先前的模型修复验证](https://github.com/m5agent/agent-work-logs/blob/db7c1d8b4e876b665aaa3267ae04a7de4709e20a/records/firmware-review-service/2026-11-09-cardputer-adv-mp3-startup/followups/2026-11-09-cardputer-adv-model-fidelity/report.md)

## 文件

- [报告](report.md)
- [结构化状态](run.json)
- [执行摘要](evidence/execution-summary.redacted.json)

## 未覆盖项

本轮范围为审核链路和原生虚拟设备。真机、物理声学与浏览器挂卡播放为 `NOT RUN`。
