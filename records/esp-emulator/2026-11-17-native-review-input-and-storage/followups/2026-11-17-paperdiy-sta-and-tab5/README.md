# PaperDIY 读卡、Cardputer STA 与 Tab5 上游候选

2026-11-17，以隔离的 Device Service 和固件审核服务执行 virtual-device validation。

PaperDIY 的卡检测、FAT32 读写及同客体复位后读回通过。Cardputer K132 和 ADV 通过受控 STA、DHCP 与 HTTP 正向用例，错误 WPA2 凭据未获得租约。macOS 审核的 namespace 准入拒绝及离线回退通过。Tab5 上游 1.1.0 通过 DSI 正对照和原版旧 P4 CSR 单步，三份原版均未出图，常驻 Tab5 切换资格为 PARTIAL。

- [复现、结果和边界](report.md)
- [执行记录和证据 SHA-256](run.json)
- [PaperDIY SD 摘要](evidence/paperdiy-sd-summary.json)
- [Cardputer 双板 STA 摘要](evidence/native-sta-summary.json)
- [审核 namespace 负对照](evidence/reviewer-namespace-negative-summary.json)
- [Tab5 1.1.0 原版及 DSI 对照摘要](evidence/tab5-1.1.0-summary.json)
- [Tab5 DSI 正对照源码](code/dsi-control/main/probe.c)

Linux 审核正向、物理硬件、浏览器 WASM 和本文对应的常驻切换验收为 NOT RUN。本轮未提交 Burner。
