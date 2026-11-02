# [文档审查][待人工审核] Stamp LoRa-1262：接收例程的射频开关控制、LoRa速率与OOK支持声明

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

## 审查范围和验证边界

- 文档基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`。源文件定位固定到此提交；下方公开页面URL是动态内容，应以基线、文件路径及行号共同核对。
- 证据类型：现有文档、已公开原理图、芯片厂商资料或驱动源码交叉核对。
- **hardware validation: NOT RUN；virtual-device validation: NOT RUN。** 未烧录、未接线、未测量、未证明量产设备发生故障。资料矛盾与运行后果必须分别审核。
- 本 issue 为人工审核资料，不表示修复完成或硬件验证通过。

## 1. 资料层已确认：接收例程把开关供电当作收发方向选择

位置：[static/zh_CN/arduino/projects/stamp/stamp_lora-1262.md:193](https://docs.m5stack.com/zh_CN/arduino/projects/stamp/stamp_lora-1262)，对应英文/日文文件同名路径的193–195行。

现状：接收端注释为“Select the receive path”，随后执行 `digitalWrite(LORA_ANT_SW_PIN, LOW)`；发送端同脚为HIGH。产品页 [static/zh_CN/stamp/Stamp_LoRa-1262.md:111](https://docs.m5stack.com/zh_CN/stamp/Stamp_LoRa-1262) 却写SWC为高有效使能。

独立依据：

- [官方原理图第1页](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1279/S014_Stamp_LoRa-1262_Sche_page_01.png)，A5–A6：`SX_ANT_SW → R1 100Ω → U2 FM8625H VDD pin4`；`SX1262 DIO2 pin12 → R2 100Ω → U2 CTRL pin6`。因此SW脚控制供电，DIO2控制射频方向。该公开图片SHA256：`33b8e69d7e7a687563509e02a330982de90bd05f9a50b88042629e265e39e3d6`。
- [RadioLib固定提交 `9ded17063793a29a63839ff82ec95ee5397b72ee` 的SX126x.cpp:57](https://github.com/jgromes/RadioLib/blob/9ded17063793a29a63839ff82ec95ee5397b72ee/src/modules/SX126x/SX126x.cpp#L57)：LoRa初始化调用 `setDio2AsRfSwitch(true)`，与原理图CTRL链路一致。

影响：教程按字面运行会把接收端外部RF开关的VDD拉低；是否仍能靠泄漏耦合在近距离收到数据、实际衰减多少、不同装配版是否一致，均**NOT RUN**，不能写成已实测收不到包。

具体修改建议：

1. 先由硬件负责人确认S014-IF当前装配确与上述原理图一致。
2. 若一致，接收与发送阶段均保持 `LORA_ANT_SW_PIN=HIGH`；注释改为“使能外部射频开关，收发方向由SX1262 DIO2控制”。
3. 保留RadioLib DIO2控制，并在关机/休眠章节另述何时允许SW拉低。
4. 对中英日例程同步修改。

## 2. 资料层已确认：300kbps属于FSK，不能标为LoRa速率

位置：[static/zh_CN/stamp/Stamp_LoRa-1262.md:71](https://docs.m5stack.com/zh_CN/stamp/Stamp_LoRa-1262)，中英日均将最高300kbps列为LoRa programmable bitrate。

依据：[Semtech官方SX1262页面的Features](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262) 将上限分别列为LoRa 62.5kbps、FSK 300kbps。这是器件规格核对，不是本模组吞吐实测。

修改建议：拆成“LoRa调制比特率：最高62.5kbps”和“FSK调制比特率：最高300kbps”，并明确实际应用吞吐还取决于带宽、扩频因子、编码率及包开销。不要把两种模式的最大值混用。

## 3. 待人工确认：OOK支持声明缺少官方依据

位置：[static/zh_CN/stamp/Stamp_LoRa-1262.md:31](https://docs.m5stack.com/zh_CN/stamp/Stamp_LoRa-1262)、73行，中英日均包含OOK。

依据：

- [Semtech官方支持列表](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262) 未列OOK。
- [Semtech/Lora-net官方driver固定提交 `a10c5dfdf89788c6ac805e9fe98889de44175aa2`，sx126x.h:255–260](https://github.com/Lora-net/sx126x_driver/blob/a10c5dfdf89788c6ac805e9fe98889de44175aa2/src/sx126x.h#L255) 的packet type枚举为GFSK、LoRa、BPSK、LR-FHSS，无OOK项。

结论边界：这些证据足以要求说明OOK来源，不足以证明任何特殊波形生成方法都绝对不可能。建议硬件/驱动维护人提供受支持API、具体模式和可复现案例；无依据时删除OOK声明，不把芯片与其他SX系列能力混用。

## 建议验收清单

- [ ] 人工确认S014/S014-I/S014-IF的当前原理图/BOM版本及SW使能逻辑。
- [ ] 中英日产品页与接收/发送例程同步，速率按调制方式分列。
- [ ] OOK声明有明确官方依据和受支持实现，或删除。
- [ ] 实际使用两套指定主控与S014-IF，在相同RadioLib版本下执行原例程和修订例程对照；记录编译配置、固件SHA256、串口标记、发包序号/收包计数和SW引脚状态。
- [ ] 确认双向收发与休眠恢复；未经射频设备测量，不声称灵敏度、输出功率或RF性能通过。
- [ ] 结果准确标注hardware validation或获批准且覆盖相同路径的virtual-device validation；目前两者均NOT RUN。
