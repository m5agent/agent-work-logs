# 修复完整教程中的语法、粘贴和 API 名称破损，恢复可复制执行的示例

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

审查基线：`nuxt-m5-docs@47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`，日期：2026-11-02。以下项限定为文档内容中的确定破损；尚未宣称对应外设功能通过硬件或虚拟设备验收。

## 问题与具体修复

| 项目 | 位置与基线现象 | 具体修复方案 |
| --- | --- | --- |
| StackChan NFC 标签模拟，中文 | [static/zh_CN/arduino/stackchan/nfc.md:449](https://docs.m5stack.com/zh_CN/arduino/stackchan/nfc)：449 行出现 `0x#include <M5StackChan.h>` 并重复程序头部；398 行外层条件缺少闭合 | 删除重复残段，以英/日完整示例和官方 NFC 示例核对后恢复单份完整程序。不要只补一个 `#endif`，那会保留损坏/重复内容。 |
| StickC RTC 日期 API，英文 | [static/en/arduino/m5stickc/rtc.md:93](https://docs.m5stack.com/en/arduino/m5stickc/rtc)、[static/en/arduino/m5stickc/rtc.md:127](https://docs.m5stack.com/en/arduino/m5stickc/rtc)、[static/en/arduino/m5stickc/rtc.md:131](https://docs.m5stack.com/en/arduino/m5stickc/rtc) 使用 `SetDate/GetDate`，而实际 M5StickC RTC API 是 `SetData/GetData` | 将标题、原型、调用统一改为所依赖 M5StickC 版本实际提供的 `SetData/GetData`；不要套用其他 RTC 库命名。 |
| StickC RTC 日期参数类型，三语言 | 日期 API 原型均标 `RTC_TimeTypeDef*`，而实际参数为 `RTC_DateTypeDef*` | 三语言日期 setter/getter 原型改为 `RTC_DateTypeDef*`，与下方 `DateStruct` 及官方头文件一致。 |
| Modbus Master 完整示例，三语言 | `static/{zh_CN,en,ja}/uiflow/blockly/advanced/modbus_master.md:23` 含无取值的 `timeout=` | 根据当前 UIFlow1 API 设置明确超时，或使用该版本已确认的默认超时；同页功能说明使用 `timeout=2000`，仍应对照实际驱动确认单位和支持。 |
| Hat 8Servo v1.1 完整示例，三语言 | `static/{zh_CN,en,ja}/uiflow/blockly/hat/8servo_v1.1.md:18` 创建 `hat_servos_1`，20 行起调用未定义 `hat_8servos_2`；中文22行还缺少对象，仅剩 `.write_servo_angle(1,0)` | 从 UIFlow1 对应 v1.1 型号重新生成完整例程；统一实例名，恢复中文对象引用，并核对 `hat.get(...)` 型号枚举及 `set_pwr_ctrl` 是否属于 v1.1 驱动。不要仅做变量替换后就判定驱动兼容。 |
| COMMU 完整示例，英文 | [static/en/uiflow/blockly/module/commu.md:41](https://docs.m5stack.com/en/uiflow/blockly/module/commu) 把右移写成非法 `>>\|` | 参考中文/日文同一发送字节构造式，将两个位置恢复为 `>>`。 |
| StickV MaixPy LCD Draw，中文/日文 | `static/{zh_CN,ja}/guide/stickv/maixpy.md:832` 写成 `fimport lcd,math,image` | 恢复 `import lcd, math, image`，以该版本 MaixPy 的模块可用性重新执行完整示例。 |

上表不把零散 API 片段要求为独立程序；所列破损均出现在页面声称可运行的完整示例或 API 原型内。

## 固定版本源码依据

官方 [M5StickC RTC.h，提交 `990489188ec40c2bd4611cc3f3f2ac7c3817024a`](https://github.com/m5stack/M5StickC/blob/990489188ec40c2bd4611cc3f3f2ac7c3817024a/src/RTC.h#L27) 定义：

```cpp
void SetData(RTC_DateTypeDef* RTC_DateStruct);
void GetData(RTC_DateTypeDef* RTC_DateStruct);
```

该头文件中没有 `SetDate/GetDate`；不能因为英文名称更自然，就反向修改中文/日文正确的方法名。中文、英文、日文的日期原型分别见 [static/zh_CN/arduino/m5stickc/rtc.md:78](https://docs.m5stack.com/zh_CN/arduino/m5stickc/rtc)、[static/en/arduino/m5stickc/rtc.md:77](https://docs.m5stack.com/en/arduino/m5stickc/rtc)、[static/ja/arduino/m5stickc/rtc.md:78](https://docs.m5stack.com/ja/arduino/m5stickc/rtc)。

StackChan 损坏位置、三语言 Modbus/Hat、COMMU、MaixPy 的上述文档链接或路径均固定对应 `47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`。协议/驱动兼容性仍须由匹配固件版本决定，本文未把 UIFlow1 示例当作 UIFlow2 可用示例。

## 已执行的复现

### 1. StackChan 条件预处理损坏

从中文 `arduino/stackchan/nfc.md` 提取“标签模拟”代码块，仅为排除主机缺少嵌入式依赖而移除 `#include` 行，执行 `clang++ -E`。返回码为 1：

```text
error: unterminated conditional directive
#if defined(EMU_MIFARE_ULTRALIGHT)
```

这只证明复制出的 C++ 文本预处理条件不完整，不是完整 Arduino 编译，也不是设备 NFC 运行结果。

### 2. StickC RTC 名称错误

使用上述固定提交的原始 `RTC.h`；主机测试仅用包含 `<stdint.h>` 的空 `Wire.h` 排除缺少 Arduino Wire 依赖。执行以下调用的 `clang++ -fsyntax-only`：

```cpp
RTC rtc;
RTC_DateTypeDef date;
void check() {
    rtc.SetDate(&date);
    rtc.GetDate(&date);
}
```

编译器分别报告 `no member named 'SetDate' in 'RTC'` 和 `no member named 'GetDate' in 'RTC'`。这不是整机固件构建或运行验证。

### 3. Python 项的复现方法

提取对应完整代码块后用 `ast.parse(code)` 或 `compile(code, filename, 'exec')` 检查语法；不要导入硬件模块或触发实际舵机动作。该检查能定位 Modbus 的空 `timeout=`、中文 Hat 的行首点号、COMMU 的 `>>|`、StickV 的 `fimport`。英语/日语 Hat 的变量不一致属于运行名称解析问题，应再用静态名称检查或与实际驱动对象一致的隔离执行验证。

本文作者未对本节所有 Python 项重新执行完整运行，不能将复现方法当作通过硬件验收的结果。

## 建议修复流程

1. 固定每个示例适用的设备、UIFlow1/MaixPy/Arduino 平台、库/固件版本；按原平台恢复示例，避免升级 API 扩大变更。
2. 对三语言同一示例共享代码或建立代码块一致性检查；正文可翻译，函数名、类型、对象名不应因翻译漂移。
3. 运行 Python 语法与名称检查、C++ 预处理/完整编译，再在匹配硬件或获准虚拟设备上执行用户相同路径。
4. Hat8Servo 涉及物理运动，运行验收采用明确供电、空载/受控负载和小角度边界，保存实际驱动 API 及行为证据后再给功能结论。

## 验收清单

- [ ] 上表每个完整 Python 示例通过适用语法检查，无未定义的示例实例名；Hat v1.1 枚举/方法与对应实际驱动匹配。
- [ ] StackChan 标签模拟代码仅有一份程序，所有条件预处理配对完整，使用页面所列真实依赖完整编译通过。
- [ ] StickC 三语言原型一致，英文日期示例使用实际存在的 API，使用固定依赖完整编译通过。
- [ ] 三语言对应代码块在应相同处一致，差异均有平台/版本理由。
- [ ] 在匹配硬件或虚拟设备上执行修改后的同一用户路径，分别保存 RTC读写、Modbus请求/响应、舵机控制、COMMU数据和LCD绘图的适用证据。
- [ ] 明确标记未接入/未运行的外设项，避免以整体 PASS 掩盖部分未验收。

## 验证分层

| 层次 | 当前结果 |
| --- | --- |
| 文档与固定版本 API 对照 | PASS：已确认上述文本破损/名称差异。 |
| StackChan 主机条件预处理复现 | PASS：重现基线 `unterminated conditional directive`。 |
| StickC 官方头文件主机语法复现 | PASS：重现两个不存在的方法错误。 |
| 全部示例完整固件构建 | NOT RUN。 |
| 修改后的构建、运行与功能回归 | NOT RUN：本 issue 尚未实施修复。 |
| hardware validation / virtual-device validation | NOT RUN：本文没有外设功能验收结论。 |
