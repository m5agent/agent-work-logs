# Tab5 UserDemo V0.4 的 Device Service 播放取证

2026-11-18 · Tab5 GT911/ILI9881C · virtual-device validation

未修改的 UserDemo V0.4 在隔离的 Device Service 1.92.0 冻结包中进入仪表盘。通过 GT911 点击 Music Test 和播放后，停机时从标准 HTTP 接口读到 48 kHz 双声道 PCM。相同观察时长的空闲对照在动作标记后采样全为零。

**PASS（隔离原生 Device Service）**。录音默认关闭，对明确配置的单一原版 Flash 哈希可显式开启，租约最长 180 秒且不可续期。浏览器、实体扬声器和 Reviewer 保存快照验证均为 NOT RUN。

[执行报告](report.md) · [机器记录](run.json) · [冻结包复验](evidence/final-http.summary.json) · [录音准入](evidence/speaker-policy.summary.json) · [旧固件回归](evidence/legacy-route-comparison.summary.json)
