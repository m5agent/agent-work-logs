# [文档审查][待人工审核] Hat ADC v1.1：芯片输入量程与ADS1110/ADS1100对比表矛盾

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

## 审查范围和验证边界

- 文档基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`。源文件定位固定到此提交；下方公开页面URL是动态内容，应以基线、文件路径及行号共同核对。
- 证据类型：现有文档、已公开原理图、芯片厂商资料或驱动源码交叉核对。
- **hardware validation: NOT RUN；virtual-device validation: NOT RUN。** 未烧录、未接线、未测量、未证明量产设备发生故障。资料矛盾与运行后果必须分别审核。
- 本 issue 为人工审核资料，不表示修复完成或硬件验证通过。

## 1. 资料层已确认：ADS1110并非±5V差分满量程

位置：[static/zh_CN/hat/Hat_ADC_v1.1.md:17](https://docs.m5stack.com/zh_CN/hat/Hat_ADC_v1.1) 声称芯片本身支持-5V至+5V差分；同页110行又写±2.048V。中英日均需核对。

独立依据：

- [TI ADS1110 datasheet SBAS276A](https://www.ti.com/lit/ds/symlink/ads1110.pdf)，第1页General Description、第3页Electrical Characteristics：差分满量程为`±2.048/PGA V`，单个模拟输入的工作范围为`GND−0.2V`至`VDD+0.2V`；第2页绝对最大额定值不能当作正常测量范围。
- [Hat ADC v1.1官方原理图第1页](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/582/StickHat_ADC_v1.1_sch_01.png)，U1供电3.3V；R3=510kΩ/R4=100kΩ构成输入分压；VIN−通过R5=0Ω接地。图片SHA256：`5cf49dc14fe1c9d21a0d7745b322b074886e96b425380805d42fbae5cf996edf`。

影响：混淆板级外部端子0–12V量程、芯片差分满量程、单脚对地电压范围，可能导致错误接线或错误的数字码到电压换算。没有执行过压/负压注入，不声称已造成损坏。

修改建议：

1. 删除“芯片本身支持±5V”。
2. 分列“成品端子输入范围0–12V直流”和“ADS1110芯片差分范围±2.048/PGA V”，说明板级分压与增益关系。
3. 明确当前接地单端输入结构，不把ADC支持双极性差分码解释为外部端子允许负对地电压。
4. 由维护人复核实际分压电阻、输入阻抗/加载误差及校准方式后，再决定是否公布精确换算公式。

## 2. 资料层已确认：产品对比表错误描述地址、增益和采样率

位置：[static/zh_CN/hat/Hat_ADC_v1.1.md:108](https://docs.m5stack.com/zh_CN/hat/Hat_ADC_v1.1)、111、113行。

| 字段 | 当前表述 | 可核对结论 |
| --- | --- | --- |
| ADS1110地址 | 四个选项，ADDR0/ADDR1 | 芯片有8种出厂固定地址料号，无ADDR0/1引脚；成品地址需以实际装配料号为准 |
| ADS1100地址 | 四个选项，ADDR | TI列8种出厂地址；无用户地址选择脚 |
| ADS1100增益 | 固定1 | PGA可编程1/2/4/8 |
| ADS1100数据率 | 固定128SPS | 可编程8/16/32/128SPS |

依据：

- ADS1110上述datasheet第2页Package/Ordering Information列A0–A7料号，Addressing章节说明地址位在工厂固定；六脚引脚表无地址脚。若PDF重新排版，以章节标题而非页码偏移为准。
- [TI ADS1100产品页Features/Description](https://www.ti.com/product/ADS1100) 与[ADS1100 datasheet Rev.B](https://www.ti.com/lit/ds/symlink/ads1100.pdf) 第1页列可编程PGA、8–128SPS及8种地址；本库 [static/zh_CN/hat/Hat_ADC.md:26](https://docs.m5stack.com/zh_CN/hat/Hat_ADC)、28行也与该对比表冲突。

修改建议：按芯片厂商资料重写表格，表格标题明确“芯片能力”与“成品板卡能力”的区别；成品0x48不写成用户可通过不存在的ADDR脚切换。不要仅修四个/八个数字而保留错误改址方法。

## 建议验收清单

- [ ] 中英日相同页面同步修正，正文与对比表不再自相矛盾。
- [ ] 硬件负责人核对实际ADS1110完整料号、地址、分压与输入连接。
- [ ] 对比表每个单元格能对应到TI datasheet或成品BOM，移除不存在的地址引脚。
- [ ] 后续以安全范围内的已知正电压点验证示例换算，在不同PGA设置下确认范围及饱和行为，记录参考仪器/误差、固件哈希和串口输出。
- [ ] 负压、过压和破坏性测试不作为文档修订的默认验收要求。
- [ ] hardware validation与virtual-device validation当前均NOT RUN；不能把静态资料核对写成测量精度验收。
