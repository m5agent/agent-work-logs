# [文档审查][待人工审核] Hat SPK2：板级供电与功率条件、采样率及音频格式需统一

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

## 审查范围和验证边界

- 文档基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`。源文件定位固定到此提交；下方公开页面URL是动态内容，应以基线、文件路径及行号共同核对。
- 证据类型：现有文档、已公开原理图、芯片厂商资料或驱动源码交叉核对。
- **hardware validation: NOT RUN；virtual-device validation: NOT RUN。** 未烧录、未接线、未测量、未证明量产设备发生故障。资料矛盾与运行后果必须分别审核。
- 本 issue 为人工审核资料，不表示修复完成或硬件验证通过。

## 1. 资料层已确认：192kHz与同页96kHz矛盾

位置：[static/zh_CN/hat/Hat_SPK2.md:19](https://docs.m5stack.com/zh_CN/hat/Hat_SPK2)、23行写32–192kHz，50行写8–96kHz。

独立依据：[ADI MAX98357A/MAX98357B datasheet Rev.16](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX98357A-MAX98357B.pdf)，第1页General Description/Features将支持采样率限定在8–96kHz。建议中英日统一为芯片实际支持的离散采样率/范围，不保留192kHz承诺。

## 2. 资料层已确认：当前原理图由3.3V轨供电，产品表却写4.5–5.5V

位置：[static/zh_CN/hat/Hat_SPK2.md:47](https://docs.m5stack.com/zh_CN/hat/Hat_SPK2)；44行“最大3.2W”也没有供电、负载及失真条件，19行板载喇叭则为1W。

依据：

- [官方原理图第1页](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/580/Sch_Hat_SPK2_sch_01.png)，P1.7主机3V3直连U1 MAX98357AETE的VDD pins7/8，P1.2 5VOUT未使用。图片SHA256：`3a8a0f63cea8b1ceb2d15f2246509553e876b064a8a5a69d2bd45267f6136e2a`。
- ADI上述datasheet第1页的3.2W能力具有`5V、4Ω`条件，不是3.3V板卡配板载1W喇叭的无条件输出额定值。芯片允许的2.5–5.5V范围也不能直接当成成品供电入口说明。

修改建议：硬件负责人先核对当前量产BOM/PCB是否仍与本页原理图相符；若一致，产品页写“由主机3.3V轨供电”，保留板载喇叭1W规格；如果需要列芯片3.2W能力，应独立注明5V/4Ω及datasheet对应失真条件，不暗示可向主机3V3脚接5V或保证成品3.2W。若板卡已改版，先更新原理图/版本说明，再决定参数。

## 3. 资料层已确认：A/B芯片格式能力被混为一项

位置：[static/zh_CN/hat/Hat_SPK2.md:24](https://docs.m5stack.com/zh_CN/hat/Hat_SPK2)、49行同时列I²S、左对齐、右对齐。

依据：原理图U1为MAX98357AETE；ADI上述datasheet第1页及第19页“I²S and Left Justified Mode”将A版I²S与B版左对齐区分。左右声道选择/混音也不等于左右对齐的数据时序格式。当前资料未提供MAX98357A支持右对齐的依据。

修改建议：按实际A版写I²S支持；若保留TDM需具体列支持的帧/字长/slot配置与验证范围。删除无依据的左/右对齐承诺，不把A/B替代芯片能力或输出声道选择混用。

## 影响与结论边界

用户可能按192kHz或错误数据对齐配置I²S，或按5V/3.2W理解板卡供电和带载能力。本文只确认文档与厂商资料/图纸不一致，未复现无声、失真、过热或损坏，未测量实际声功率。

## 建议验收清单

- [ ] 人工确认现有出货版本的U1完整料号、供电轨、喇叭阻抗及额定功率。
- [ ] 中英日的描述、特性、规格表统一，无192kHz与96kHz冲突。
- [ ] 每个功率值列供电、负载、THD+N和是否芯片典型值；不以芯片最大值替代成品指标。
- [ ] 在实际板卡执行官方示例及至少一组明确支持的I²S配置，记录代码/固件SHA256、时钟/格式配置和可核对输出证据。
- [ ] 如声明功率/失真能力，另做仪器测量；音频播放成功不等于3.2W输出验证。
- [ ] hardware validation和virtual-device validation目前均NOT RUN。
