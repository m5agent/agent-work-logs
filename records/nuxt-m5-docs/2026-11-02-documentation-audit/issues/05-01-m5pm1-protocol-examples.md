# [文档审查] 修正 S021 协议页 M5PM1 温度与 NeoPixel 示例，并明确温度编码

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

## 审查范围和状态

文档基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`（当前远端 master，2026-11-02 核对）。影响中文、英文、日文 `protocol/S021/I2C.md`。本工单请求人工审核文档与公开 API 的一致性，不宣称设备固件已复现故障或修复成功。

- 文档/API 对照：REVIEW。
- 主机语法检查：原始 ADC 示例 FAIL；仅修正参数后 PASS。
- hardware validation / virtual-device validation：NOT RUN。

## 问题与可定位证据

1. [中文 ADC 示例第697行](https://docs.m5stack.com/zh_CN/protocol/S021/I2C) 调用 `pm1.readTemperature(M5PM1_ADC_CH_TEMP, &temp_value)`；[英文](https://docs.m5stack.com/en/protocol/S021/I2C)和[日文](https://docs.m5stack.com/ja/protocol/S021/I2C)相同。
2. [NeoPixel 示例第674–680行](https://docs.m5stack.com/zh_CN/protocol/S021/I2C) 用 `setLeds(&rgb_red, 1, 3, true)` 声称把3颗灯设红，再用 `setLeds(rgb_array, 3, 1, true)` 声称设置3颗不同颜色。
3. [内部温度寄存器说明第328行](https://docs.m5stack.com/zh_CN/protocol/S021/I2C) 直接将结果单位写成 °C，但公开 Arduino 头文件写0.1°C。这里需要确认权威编码，不能直接用其中一份注释覆盖其他资料。

独立依据固定到 M5PM1 `315d2899c863ae34b59197392b9f4c59490751ef`，`library.properties` 为1.0.7：

- [readTemperature声明](https://github.com/m5stack/M5PM1/blob/315d2899c863ae34b59197392b9f4c59490751ef/src/M5PM1.h#L1559)：只接受一个 `uint16_t*`。
- [setLeds声明与参数](https://github.com/m5stack/M5PM1/blob/315d2899c863ae34b59197392b9f4c59490751ef/src/M5PM1.h#L2395)：依次为颜色数组、数组长度、LED数量、是否刷新。
- [setLeds实现](https://github.com/m5stack/M5PM1/blob/315d2899c863ae34b59197392b9f4c59490751ef/src/M5PM1.cpp#L4365)：`count > arraySize` 返回 `M5PM1_ERR_INVALID_ARG`；按 `count` 写LED。故前三个调用在已初始化条件下被参数校验拒绝，最后一个只配置一颗。
- [温度注释及实现](https://github.com/m5stack/M5PM1/blob/315d2899c863ae34b59197392b9f4c59490751ef/src/M5PM1.h#L1552)：头文件写0.1°C，实际实现将通道6读数直接返回。[实际实现](https://github.com/m5stack/M5PM1/blob/315d2899c863ae34b59197392b9f4c59490751ef/src/M5PM1.cpp#L2915)直接返回通道6读数。需要芯片固件负责人确认真实单位、符号和转换公式。

## 复现与影响

提取协议页13.3节完整ADC代码，使用上述官方头文件进行 `clang++ -std=c++17 -DARDUINO -fsyntax-only`。主机只补充平台 `Wire` 声明，不修改M5PM1 API。原始代码报告：

```text
error: too many arguments to function call, expected single argument 'temperature', have 2 arguments
```

改成 `pm1.readTemperature(&temp_value)` 后该代码段通过同一语法检查。这是API层证据，不是完整Arduino构建或设备验证。

按文档复制NeoPixel参数无法得到注释承诺的三灯显示；该影响由当前库的确定控制流推导，尚未采集设备返回码或灯光行为。

## 建议修改

1. 为Arduino案例注明已核对的M5PM1版本，并将温度调用改为：

```cpp
pm1.readTemperature(&temp_value);
```

2. 单色三灯也准备三元素数组，数组长度和LED数量均传3，例如：

```cpp
m5pm1_rgb_t red[3] = {{255, 0, 0}, {255, 0, 0}, {255, 0, 0}};
pm1.setLeds(red, 3, 3, true);
pm1.setLeds(rgb_array, 3, 3, true);
```

3. 保留初始化、GPIO0复用/推挽与刷新等待的前提，检查每个调用返回码。确认温度编码后统一寄存器章节、Arduino和MicroPython说明；若未确认，明确写为待确认原始值，不给未经核实的摄氏温度换算。
4. 同步中英日三语代码和注释，避免继续直接复制旧数据手册中的失配示例。

## 人工验收清单

- [ ] 三语代码与同一明确版本的M5PM1头文件匹配，完整Arduino工程可编译。
- [ ] 初始化成功后，三次单色三灯和一次RGB三灯的返回码均为M5PM1_OK。
- [ ] hardware validation或覆盖同路径的virtual-device validation记录灯数量、颜色数据和刷新协议；实体光学结果只有实测后再声明。
- [ ] 温度单位/符号/换算由芯片固件依据确认，并在多个资料源统一。
- [ ] 修复后同步文档知识库，以同一API问题复查，不能把知识库同源返回当作独立硬件证据。

## 验证边界

未刷机、未操作GPIO、未采集I2C事务或真实温度。此工单不证明物理灯光或温度测量精度。

## 审查记录

本文件即本次审查的归档依据；发布工单将引用本归档的完整提交永久链接。
