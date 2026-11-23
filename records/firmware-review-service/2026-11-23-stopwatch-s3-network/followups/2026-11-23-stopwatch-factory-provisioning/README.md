# StopWatch 出厂配网与 DHCP 重传摘要修复

- 日期：`2026-11-23`
- 结果：`PARTIAL`（本条原版出厂配网、复位回连及独立抓包回放通过；旧门户兼容性限制保留）
- 工作类型：`code_change`
- 问题来源：[此前网络审查复验](../../)
- 源码版本：见[执行清单](run.json)中的完整提交身份；本条后续源码尚未对外发布。
- 环境：macOS arm64 隔离原生 Device Service、`m5stopwatch`、私有 Unix socketpair，零宿主 IP 后端。

## 结论

相同 StopWatch Demo Plus V0.6-OPT 原版从出厂空 NVS 完成门户提交、退出配网和 STA 入网，来宾自行写入的配置经 CRC 核对；同一会话复位后无需再次提交门户即可回连。最新精确源码重放记录 3 次 DHCP DORA、2 个地址和 4 条双向 TCP payload 流。独立 PCAP 修复保留所有重传包计数，使 67 次连续 DISCOVER 不再遮住后续完整交换。

## 关键证据

- [原版及最新精确提交重放摘要](evidence/stopwatch-factory-provisioning.summary.json)：以 `exact_committed_replay` 为最新执行；较早观察仍保留。
- [出厂配网验证摘要](evidence/stopwatch-validation.summary.json)：独立全量 `2522 OK / 11 skip`。
- [同一 A1 抓包回放](evidence/pcap-dhcp-replay.summary.json)：统计由 DORA `0`、双向 TCP `0` 修正为 `1`、`2`；A1 原应用结论仍为 `PARTIAL`。
- [PCAP 修复验证摘要](evidence/pcap-validation.summary.json)：另一源码切面的独立全量 `2522 OK / 11 skip`。

## 文件

- [完整报告](report.md)
- [结构化执行清单](run.json)
- `evidence/`：仅有界、已脱敏派生摘要；不包含原始抓包、画面、Flash、凭据或第三方固件。

## 未覆盖项

本条两项后续变更未在 Linux 或常驻服务部署，未验证浏览器、物理硬件、WPA2、外网或任意门户。此前[已配网 STA 常驻路径](../2026-11-23-resident-sta-cutover/)是独立里程碑。旧 StickS3 门户在新旧 runtime 上都只得到 `PARTIAL`，不能据此归因补丁回归或宣布旧门户完成。未提交 Burner。
