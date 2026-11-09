# EMBER 2.1 独立应用镜像虚拟审核复验

- 日期 `2026-11-09`
- 工作类型 `code_change`
- 总体状态 `PARTIAL`
- 设备 Cardputer ADV
- 环境 Device Service 原生 QEMU
- 上游固件与配置对应固定提交 `d34949441e77430239a27248bbbcc47601558431`。[EMBER 源码](https://github.com/HorseyofCoursey/EMBER/tree/d34949441e77430239a27248bbbcc47601558431)

审核旧入口将带 ESP 应用描述符的独立 BIN 按整盘镜像导入，在偏移 `0x8000` 误查分区表，并丢失了嵌套诊断。此次按可核验的厂商配方重建引导前缀，并校验原始应用字节。

常驻审核 dry-run 结束为 `SIM_VERIFIED`，并回读验证了原应用及启动段。Cardputer ADV 虚拟设备读到 SD 测试曲目，Enter 触发播放，输出 PCM 与参考频率匹配。通用幅值门槛仍未通过。此次未提交 Burner。

[报告](report.md) · [结构化运行记录](run.json) · [脱敏证据](evidence/execution-summary.redacted.json)

实物硬件及浏览器路径为 `NOT RUN`。
