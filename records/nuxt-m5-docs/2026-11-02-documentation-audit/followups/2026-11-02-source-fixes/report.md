# 全部开放文档Issue源码修订报告

## 目标与范围

用户要求修复当前所有开放issue并提交一个人工审核MR。查询时共13项，包括此前的Basic知识库口径问题。基于 `47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac` 创建独立分支工作区，4个逻辑提交形成 `00eee6d573af4259e4fb9052b77ebef1dbe7b47e`，共120文件；未合并主分支、未改生产部署。

## 具体变化

| Issue | 修改范围 | 当前边界 |
| --- | --- | --- |
| #1 | Basic SKU facts and both knowledge ingestion paths | Source corrected; production sync, chatbot rewrite service and online retest pending |
| #2 | LoRa RF switch control and modulation specifications | Three languages corrected; RF runtime NOT RUN |
| #3 | ADC chip and terminal ranges, fixed addresses and comparison | Three languages corrected against TI data and schematic |
| #4 | SPK2 supply, power conditions, format and sample rates | Three languages corrected against schematic and ADI data |
| #5 | SSR, relay supply, DAC isolation and charging semantics | Misleading statements corrected; charging BOM, cutoff voltage and current-state mapping still require product-owner confirmation |
| #6 | M5PM1 API, RGB arguments and temperature interpretation | Three languages corrected; unknown Celsius conversion is no longer implied |
| #7 | BMI270 zero-offset terminology and conditions | Three languages corrected with specified Bosch datasheet conditions |
| #8 | UIFlow1 links, compatibility redirects and empty translations | 24 entries and two translated bodies corrected; 21 distinct redirects checked |
| #9 | Broken complete examples and RTC APIs | Syntax/name corruption corrected; parser, preprocessor and header probes passed |
| #10 | LLM630 translations and Gray recovery link | Translations completed; unused local MJPEG scaffold removed; documented Gray link aligned, device recovery NOT RUN |
| #11 | Chain right-port UART mapping | Actual example and 24 tutorial comments corrected |
| #12 | EXTIO2 input mode, formatting and pin description | Three languages corrected; device loopback NOT RUN |
| #13 | INA226, DoF10 and AIN4-20mA data semantics | Results, cache timing and units corrected; sensor runtime NOT RUN |

额外修正同一批页面检查中发现的空图片/购买占位链接、StickV残留括号/重复片段，以及DAC2地址上限的同页矛盾。这些是相关页面的最小完整性修正，不宣称它们都已出现在最初工单正文。

## 知识库输入修订

只对两份固定路径的M5Unified导入摘要应用SKU说明与板卡表行拆分，保留其他板卡、PMIC地址索引和普通文件行为。CSV读取与ESP上传共用同一内容函数；对象key不变，规范化哈希与实际临时上传文件一致。真实两份ignored输入已离线验证原文件字节不变、SKU说明进入CSV、哈希匹配且规则幂等。测试覆盖PMIC索引保护、实际导入前导纯文本、BOM/CRLF、非UTF8普通文件和重复同步收敛，不发生远端写入。

## 验证结果

- 修改的110份Markdown通过现有html_format_check。
- 新增8项知识库回归测试PASS；全套23项中22项通过。`test_known_dead_pdf_is_excluded`在修改前15项基线中也失败，属于已有测试/旧PDF规则不一致，未借本次扩大修改。
- 三语M5PM1改后片段对固定官方头文件syntax-only 3/3 PASS；仅替换平台声明，无设备运行。
- 186个涉及页面Python代码块解析、1119个UIFlow目录目标、21个精确兼容跳转、query保留/无循环通过。
- NFC两种宏分支预处理和RTC修正API官方头文件语法检查通过。
- LLM630标准库TCP客户端在隔离主机fixture完成setup/link/inference/exit、UTF8分包与流式文本检查。这是host fixture，不是虚拟设备。
- UTF8、JSON与保留CRLF的diff检查通过。

## 未执行及人工审核重点

设备验证、RF/电气/光学性能和完整Arduino草图编译均NOT RUN。完整Nuxt构建未执行（项目要求Node14，现有主机运行时Node22且没有完整应用依赖）。分支CI配置没有自动运行的文档检查任务，生产发布任务仅master适用；不触发生产CI或部署。

合并后按正常发布流程更新网站和知识库，并复测Basic三条原始问法。query rewrite由独立服务控制，本仓库修订不能证明该服务已更改。Timer Power2的实际完整充电器料号、截止电压、档位映射及M5PM1温度单位由负责人依据对应版本确认；修订不擅自补值。Gray链接对齐已记录的恢复方案，实际刷机兼容尚未验证。

## 风险与回滚

知识输入规则只影响两份特定摘要；列布局改变会明确失败，不猜列或静默改坏其他表。源文档只做人工审阅修订，未操作设备。可按4个逻辑提交分别回退；不自动关闭issue、不合并MR、不上线。公开记录省略内部跟踪地址、主机路径和凭据，只保留安全摘要、公开来源以及提交哈希。
