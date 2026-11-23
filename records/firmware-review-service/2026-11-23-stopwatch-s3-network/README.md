# StopWatch 与 ESP32-S3 网络审查复验

- 日期 `2026-11-23`
- 结果 `PARTIAL`
- 工作类型 `service_debug`
- 问题来源 [固件审查过程诊断](../2026-11-23-review-process-diagnosis/)
- 源码版本见 [执行清单](run.json)
- 执行环境为隔离 Linux Device Service 与原生 ESP32-S3 QEMU

## 结论

StopWatch Demo Plus 的原版冷启动需要从设置打开 Wi‑Fi。六个真实操作可重复抵达配置热点，来宾启动了配网服务。预置实验网后，同一原版在隔离会话关联并拿到 DHCP 地址。PaperDIY 使用受控固件完成 STA 关联与 DHCP。Cardputer 与 ADV 原版保存快照通过候选 Reviewer 进入隔离会话，原版的联网功能仍待有效的数据面证据。S3-watch 在长按 B 后显示 Web 地址。

## 证据与范围

- [完整报告](report.md)
- [执行清单](run.json)
- [脱敏验证摘要](evidence/validation-summary.redacted.json)
- [StopWatch 原版已配网复审请求参数](code/stopwatch-preconfigured-validation.json)

未运行物理硬件。常驻服务部署和 Burner 提交均未执行。
