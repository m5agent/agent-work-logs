# M5Stack 文档全库审查与人工工单证据包

- 日期：2026-11-02（Asia/Shanghai）
- 结果：REVIEW；资料/源码对照完成，设备功能未验收。
- 工作类型：issue / report。
- 对象：公开文档 https://docs.m5stack.com ，三语文档及相关官方库。
- 文档源码基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`；最初扫描基线 `5ff5afc0319beee52ea70f34916f06a91cac735e`，发表前已对照新基线复查。
- 环境：本地主机进行源码阅读、HTTP GET、Python语法解析及C++头文件语法/预处理检查；未操作设备。

## 结论

本记录归档12组供人工审核的文档问题。用户针对本批工单明确允许以REVIEW发表，并要求标注hardware validation和virtual-device validation均为NOT RUN。此授权不是设备功能验证，也不表示文档已修复。

## 工单证据包

| 编号 | 主题 | 证据 |
| --- | --- | --- |
| DOC-01 | [文档审查][待人工审核] Stamp LoRa-1262：接收例程的射频开关控制、LoRa速率与OOK支持声明 | [详情](issues/01-01-stamp-lora1262.md) |
| DOC-02 | [文档审查][待人工审核] Hat ADC v1.1：芯片输入量程与ADS1110/ADS1100对比表矛盾 | [详情](issues/02-02-hat-adc-v11.md) |
| DOC-03 | [文档审查][待人工审核] Hat SPK2：板级供电与功率条件、采样率及音频格式需统一 | [详情](issues/03-03-hat-spk2.md) |
| DOC-04 | [文档审查][待人工审核] 电气能力表述：SSR过零时序、2Relay供电、DAC2隔离与Timer Power2充电条件 | [详情](issues/04-04-electrical-semantics.md) |
| DOC-05 | [文档审查] 修正 S021 协议页 M5PM1 温度与 NeoPixel 示例，并明确温度编码 | [详情](issues/05-01-m5pm1-protocol-examples.md) |
| DOC-06 | [文档审查] DoF6/DoF9/DoF10 的 BMI270 零偏不应标成全局测量精度 | [详情](issues/06-02-bmi270-spec-terminology.md) |
| DOC-07 | 修复 UIFlow1 的 24 处错链入口和英日 LoRa Bus 空白正文 | [详情](issues/07-01-uiflow1-routes-and-empty-pages.md) |
| DOC-08 | 修复完整教程中的语法、粘贴和 API 名称破损，恢复可复制执行的示例 | [详情](issues/08-02-complete-example-syntax-and-api-breakage.md) |
| DOC-09 | 补齐 LLM630 摄像头 VLM 英日教程，并审查 Gray 日文恢复固件的跨型号链接 | [详情](issues/09-03-multilingual-content-and-gray-recovery-review.md) |
| DOC-10 | [文档审查] Chain DualKey 右侧 UART 示例及 24 处教程注释的 RX/TX 映射颠倒 | [详情](issues/10-01-chain-dualkey-uart.md) |
| DOC-11 | [文档审查] EXT.IO2 数字输入例程未配置输入通道，且三段例程的 printf 参数类型错误 | [详情](issues/11-02-extio2-example.md) |
| DOC-12 | [文档审查跟踪] 修正 INA226、DoF10 与 AIN4-20mA 示例的测量结果来源、更新标志和单位语义 | [详情](issues/12-03-measurement-semantics.md) |

## 工单交付

12/12已发表并逐条回读，编号#2–#13全部opened，正文仍标REVIEW与设备NOT RUN。详见[独立交付记录](followups/2026-11-02-issue-delivery.md)及[脱敏交付摘要](evidence/issue-delivery-summary.json)。

## 关键证据与导航

- [report.md](report.md)：范围、方法、发布边界、复查和修复验收要求。
- [run.json](run.json)：分层状态。
- [HTTP观察](evidence/http-observations.json)：公开站点错误入口、正确目标和空正文的实际响应。
- [验证摘要](evidence/validation-summary.json)：语法/API对照与未执行项。
- [可重复的Python语法检查](code/check_document_examples.py)及[本次输出](evidence/python-syntax-observations.json)。
- [源文件定位](evidence/source-locations.json)：审查提交、文件和行号。
- [工单清单](evidence/issue-manifest.json)：12组标题与状态。
- patches：不适用。本次只提交人工审核工单，没有修改文档或固件。

## 未覆盖项

hardware validation、virtual-device validation、RF/电气/光学测量和修复后的完整构建/部署均NOT RUN。第三方资料仅链接或概述，不复制数据手册或固件全文。公开副本不包含内部跟踪系统地址或设备标识。
