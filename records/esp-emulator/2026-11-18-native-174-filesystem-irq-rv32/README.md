# Device Service 1.74 原生复验与输入时序追踪

- 日期 `2026-11-18`
- 整体 `PARTIAL`，工作类型 `report`
- 真实来宾验证的源码 `e822150c90a99b33fbb0f437db611c04f3e1e6e3`，发行包源码 `a2148953f1c22a2b2b066780f9c501b3daddcdf0`
- 环境为隔离 Device Service、Xtensa/C6 原生运行时。较早的 Dial 和 PaperS3 时序实验另绑定原生和浏览器构建。

四组 LittleFS/SPIFFS 共 12 个来宾会话通过源数据分区导出、服务重启及新会话回读。Cardputer 的两条 GP-SPI 中断路由和 Nesso N1 的两种 UART RV32 转储通过。NC1020 在同一最终构建仍可冷导入并保存，首次完整绘制未观测到。更早的 Dial 快速旋转及 PaperS3 原版触摸诊断保留为 `PARTIAL`。

[报告](report.md) · [结构化结果](run.json) · [取证索引](evidence/README.md)
