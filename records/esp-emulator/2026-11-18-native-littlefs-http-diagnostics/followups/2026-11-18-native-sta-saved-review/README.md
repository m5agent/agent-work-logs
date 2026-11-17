# 保存快照审核的本地 STA 应用断言

- 日期为 `2026-11-18`，类型为代码变更和虚拟设备验证
- 整单为 `PARTIAL`。Cardputer、Cardputer ADV 和 Core2 的固定本地应用断言通过
- 环境为独立的 Linux 原生 Device Service 与 Reviewer 0.13.0，使用三个板型的已知测试固件

Cardputer ADV 同固件收到单字节不同的二进制 UDP 响应时，来宾拒绝响应，应用断言为 `FAIL`。缺少私有网络命名空间的对照在分配网络租约前终止。无画面夹具的整单审核均保留 `E_NO_FRAME`。实机、浏览器、互联网、常驻部署及 Burner 提交均未执行。

[报告](report.md) · [运行清单](run.json) · [有界证据](evidence/README.md)
