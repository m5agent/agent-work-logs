# [文档审查][待人工审核] 电气能力表述：SSR过零时序、2Relay供电、DAC2隔离与Timer Power2充电条件

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

## 审查范围和验证边界

- 文档基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`。源文件定位固定到此提交；下方公开页面URL是动态内容，应以基线、文件路径及行号共同核对。
- 证据类型：现有文档、已公开原理图、芯片厂商资料或驱动源码交叉核对。
- **hardware validation: NOT RUN；virtual-device validation: NOT RUN。** 未烧录、未接线、未测量、未证明量产设备发生故障。资料矛盾与运行后果必须分别审核。
- 本 issue 为人工审核资料，不表示修复完成或硬件验证通过。

## A. 资料层明确问题：过零SSR不能无条件承诺微秒级负载通断

位置：[static/zh_CN/unit/Unit_SSR.md:15](https://docs.m5stack.com/zh_CN/unit/Unit_SSR)，英文同页也写microsecond-level switching speed；产品同时明确采用MOC3043零交越驱动与BT136S TRIAC。

依据：[页面链接的Fairchild MOC303XM/MOC304XM原厂datasheet](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/datasheet/unit/ssr/C41809_MOC3043SR2M_2015-01-24.PDF)，Rev.1.0.7，第1页Description、第3页Zero Crossing Characteristics：这是零电压交越双向可控硅驱动器，主端电压超过抑制阈值时不触发。

结论：数字控制信号变化到负载导通的延迟取决于交流相位，不能笼统保证微秒级；TRIAC关断也涉及负载电流降至保持电流以下。以50Hz半周期10ms说明相位影响属于波形推导，**不是产品测量结果**。

修改建议：删除无条件“微秒级通断速度”；改为零交越开关说明，区分光耦内部响应与实际负载通断，说明不作为任意相位调光/高频PWM开关。后续若给响应时间，应列交流频率、负载类型、控制相位与测量方法。

## B. 需明确修辞的问题：2Relay“支持交直流电源输入”混淆控制供电与被控线路

位置：[static/zh_CN/module/Module13.2_2Relay.md:26](https://docs.m5stack.com/zh_CN/module/Module13.2_2Relay)，“电源输入（支持交直流输入）”；47行又笼统写“电气特性：交直流电”，49行仅给250VAC@5A，未列DC额定范围。

独立依据：[官方原理图第1页](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/551/Sch_Module13.2_2Relay_sch_01.png)：

- 控制器由M5-Bus J1 pin12的3.3V供电；继电器线圈由J1 pin28的5V供电。
- P4/P5接K1/K2独立SPST触点；触点没有连接到控制侧电源/地。
- 图面没有给控制电路提供交流输入整流或AC/DC电源。图片SHA256：`957ed87dcd0e2163f36c5b33a1c32848e94dd9d686eb26cd4969b7b17c2cf5de`。

建议：将该特性改为“继电器触点可开断符合额定条件的交流/直流负载”，另列控制侧3.3V/5V直流供电、干接点接线图、经实际继电器完整料号确认的AC/DC额定值。不能把250VAC@5A直接套用于直流。DC能力目前待BOM/继电器datasheet人工核对，不填猜测值。

这属于高影响的接口语义澄清请求；没有向模块注入交流，也未声称存在实测损坏。

## C. 待人工确认的应用范围：DAC2的“工业模拟信号隔离”容易被当成自带电气隔离

位置：[static/zh_CN/unit/Unit_DAC2.md:16](https://docs.m5stack.com/zh_CN/unit/Unit_DAC2)、36行；[static/zh_CN/hat/Hat_DAC2.md:17](https://docs.m5stack.com/zh_CN/hat/Hat_DAC2)、38行。该术语位于用途列表，不等于文档已明确宣称某一隔离耐压，但目前未说明需要外部隔离级。

独立依据：

- [Unit DAC2官方原理图第1页](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/575/SCH_UNIT_DAC2_V1.0_sch_01.png)：主机Grove GND、GP8413 GND与输出端P1的GND为公共网络，电源是TPS61040非隔离升压。
- [Hat DAC2官方原理图第1页](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/581/SCH_StickHat_DAC2_sch_01.png)：主机P2.1 GND、U1.6 GND与输出P1.2/P1.4 GND为公共网络。

建议硬件负责人明确用途是“接入另有隔离的系统”还是误用了术语。若产品本身不提供电气隔离，将用途改为工业模拟量输出/信号转换，并明确“输入/输出共地，需要隔离时另配隔离级”；不要填写原理图未支持的隔离耐压或把TVS保护等同于隔离。

## D. 待BOM/测试条件确认：Timer Power2充电规格中的3.3V是什么条件

位置：[static/zh_CN/stamp/Stamp_Timer_Power2.md:59](https://docs.m5stack.com/zh_CN/stamp/Stamp_Timer_Power2)：`LGS4056HDA，提供 DC 3.3V@650mA / DC 3.3V@180mA 两档可调充电电流`。已直接读取最新`origin/master`确认，此处原文仍为3.3V。

歧义：3.3V未注明是电池端测试电压、输出目标还是其他条件；两个电流档位也未给CHG_PROG状态映射。当前写法容易把单节锂电充电器理解成3.3V恒压输出。

依据：页面链接的[LGS4056H原厂datasheet Rev.C V1.3](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1222/C5280698_Battery_Management_LGS4056HDA-4.35_Datasheet_LGS4056HDA-4.35.pdf)第1页Description/Ordering Information说明CC/CV充电，默认无电压后缀型号满充4.20V，另有4.35V后缀版本；[官方模组原理图第1页](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1294/S021_Stamp_Timer_Power2_SCH_V0.7.1_page_01.png)的U5标LGS4056HDA、BAT接VBAT、VCC接Internal_5V。PDF文件名含4.35不等于原理图/BOM装配了4.35版本，不能据文件名推断实际满充电压。

建议：由硬件负责人确认实际完整料号和满充目标后，单列“适配电池类型/满充电压”；若3.3V表示测量时的VBAT，明确写为测试条件；电流档位注明典型/实测或配置目标、CHG_PROG高/低/悬空对应关系。本文不主张未经BOM核对直接把3.3改成某个保证值，也没有证明量产硬件存在错误充电电压。

## 建议验收清单

- [ ] 由各产品负责人分别审核A/B/C/D，确认问题成立后可拆分跟踪，避免用一个笼统结论覆盖不同产品。
- [ ] SSR修订中区分器件响应与负载过零切换，所有时间值带明确条件。
- [ ] 2Relay有明确控制供电与触点负载接线，DC额定值由实际继电器BOM/厂商资料确认。
- [ ] DAC2明确电气隔离是否存在及系统级应用边界，三语言一致。
- [ ] 如进行后续验证，采用具备相关资格/安全条件的设备路径，记录配置、控制输入与电压/电流时序或连续性证据；不为了文档校订默认做危险/破坏性注入。
- [ ] Timer Power2确认充电器完整料号、充电截止电压、3.3V测试条件及档位映射，三语言一致。
- [ ] 资料审查通过与功能验证通过分别记录；hardware validation和virtual-device validation目前均NOT RUN。
