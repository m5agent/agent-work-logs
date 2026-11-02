# [文档审查] EXT.IO2 数字输入例程未配置输入通道，且三段例程的 printf 参数类型错误

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

## 审查基线与验证状态

- 文档仓库基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`。
- 文档：`static/{zh_CN,en,ja}/arduino/projects/unit/unit_extio2.md`，三语相关代码位置相同。
- 类型：Arduino / 用户 Example 的正常实验路径与 API 使用错误。
- 已完成：完整示例控制流、官方 EXT.IO2 驱动和 M5GFX显示格式化实现的交叉核对。
- hardware validation：**NOT RUN**。
- virtual-device validation：**NOT RUN**。
- 本文未声称已观察到设备乱码、崩溃或错误电平；这些实际表现仍需按验收方案确认。

## A. 数字输入示例没有建立“Pin0 输出、Pin1 输入”状态

### 位置与依据

`unit_extio2.md:155-213` 为完整数字输入示例：

- 第 163 行：`mode = DIGITAL_OUTPUT_MODE`。
- 第 191-192 行：`extio.setAllPinMode(DIGITAL_OUTPUT_MODE)`，所有通道都设成输出。
- 第 207 行：对 Pin0 写 HIGH。
- 第 209 行：读取 Pin1。
- 第 210 行：循环末尾又 `extio.setAllPinMode(mode)`。
- 按键逻辑也只能让所有引脚一起切到输入或一起切到输出。

第 291 行的效果说明要求“一个引脚输出高电平并用另一引脚读取”。当前示例始终没有分别设置 Pin0 输出、Pin1 输入：默认时 Pin1 是输出，切换后 Pin0 又成为输入。

独立驱动依据为 M5Unit-EXTIO2 固定版本 `fcf67c4b16e9b27f9f57ec5ec01ec01efd8e7fec`：

- [`M5_EXTIO2.cpp:53-57`](https://github.com/m5stack/M5Unit-EXTIO2/blob/fcf67c4b16e9b27f9f57ec5ec01ec01efd8e7fec/src/M5_EXTIO2.cpp#L53)：`setAllPinMode()` 将同一个模式写入全部 8 个通道的模式寄存器。
- [`M5_EXTIO2.cpp:66-70`](https://github.com/m5stack/M5Unit-EXTIO2/blob/fcf67c4b16e9b27f9f57ec5ec01ec01efd8e7fec/src/M5_EXTIO2.cpp#L66)：`setPinMode()` 可以分别配置单通道。
- [`M5_EXTIO2.cpp:141-147`](https://github.com/m5stack/M5Unit-EXTIO2/blob/fcf67c4b16e9b27f9f57ec5ec01ec01efd8e7fec/src/M5_EXTIO2.cpp#L141)：`getDigitalInput()` 只读输入状态寄存器，不会自动改变 GPIO 方向。

### 最小修改建议

数字输入实验独立设置 Pin0 输出、Pin1 输入，并去掉该实验中覆盖全部通道模式的按键任务和 `setAllPinMode(mode)`。这里不需要增加并发任务或新的抽象层。

可将数字输入代码块替换为下面的完整教学例程；其编译和设备运行仍为 **NOT RUN**：

```cpp
#include <M5Unified.h>
#include "M5_EXTIO2.h"

M5_EXTIO2 extio;

void setup() {
    M5.begin();
    Serial.begin(115200);
    M5.Display.setFont(&fonts::FreeMonoBold9pt7b);
    M5.Display.setTextColor(TFT_WHITE, TFT_BLACK);

    while (!extio.begin(&Wire, 2, 1, 0x45)) {
        Serial.println("EXTIO2_INIT_ERROR");
        delay(1000);
    }

    extio.setPinMode(0, DIGITAL_OUTPUT_MODE);
    extio.setPinMode(1, DIGITAL_INPUT_MODE);
    extio.setDigitalOutput(0, LOW);
}

void loop() {
    static bool output_high = false;
    output_high = !output_high;
    extio.setDigitalOutput(0, output_high ? HIGH : LOW);
    delay(20);
    const bool input_high = extio.getDigitalInput(1);

    M5.Display.fillScreen(TFT_BLACK);
    M5.Display.setCursor(0, 0);
    M5.Display.printf("FW VERSION: %u\n", static_cast<unsigned>(extio.getVersion()));
    M5.Display.printf("Pin0 OUT: %u\nPin1 IN: %u",
                      static_cast<unsigned>(output_high),
                      static_cast<unsigned>(input_high));
    Serial.printf("EXTIO2_LOOPBACK out=%u in=%u\n",
                  static_cast<unsigned>(output_high),
                  static_cast<unsigned>(input_high));
    delay(1000);
}
```

正文同时明确本实验在断电接线时将 EXT.IO2 的 Pin0 接到 Pin1；输入通道配置生效后再进行回环测试。若希望演示单独的外部输入，也可以让 Pin1 接按钮，删除 Pin0 输出部分，并相应修改效果说明。

## B. 三段例程向 `%s` 传入 Arduino String 对象

### 位置与依据

三语文件都存在以下三处：

- 第 136 行：`printf("FW VERSION: %s", String(extio.getVersion()))`。
- 第 209 行：`printf("Pin_1 level is %s", (String)extio.getDigitalInput(1))`。
- 第 244 行：`printf("FW VERSION: %s", String(extio.getVersion()))`。

`%s` 需要 C 字符串指针，Arduino `String` 对象通过可变参数传递时不会自动转为 `c_str()`。

独立源码依据：

- [M5GFX固定提交 `7cb26b44ab31bb41a0a597196dd2c6d868869a21` 的 `LGFXBase.cpp:2498`](https://github.com/m5stack/M5GFX/blob/7cb26b44ab31bb41a0a597196dd2c6d868869a21/src/lgfx/v1/LGFXBase.cpp#L2498)：显示对象的 `printf()` 将可变参数转发给自身 `vprintf()`。
- [同文件 `LGFXBase.cpp:2509`](https://github.com/m5stack/M5GFX/blob/7cb26b44ab31bb41a0a597196dd2c6d868869a21/src/lgfx/v1/LGFXBase.cpp#L2509)：`vprintf()` 直接调用 `vsnprintf()`，没有对Arduino String对象进行隐式字符串转换。

因此可以确认格式参数类型错误；乱码、异常或具体编译器诊断尚未运行验证，不把其中任一种表现写为实测。

### 最小修改建议

这两类数据本身是数字，推荐直接避免临时 String：

```cpp
M5.Display.printf("FW VERSION: %u", static_cast<unsigned>(extio.getVersion()));
M5.Display.printf("Pin_1 level is %u", static_cast<unsigned>(extio.getDigitalInput(1)));
```

若确需字符串格式，应使用 `.c_str()`；但这里直接使用 `%u` 更便于用户理解。

## C. CoreS3 SDA/SCL 正文与硬件、现有正确代码相反

第 27 行写 `G1 (SDA)、G2 (SCL)`。CoreS3 外部接口实际为 **G2 SDA、G1 SCL**。

[M5Unified 固定版本 `44952cb8e4ac88bf04ad23b9dfd6f4b05c788348`，`src/M5Unified.inl:97-101`](https://github.com/m5stack/M5Unified/blob/44952cb8e4ac88bf04ad23b9dfd6f4b05c788348/src/M5Unified.inl#L97) 的表头是 `In SCL,SDA, EX SCL,SDA`，CoreS3 对应外部值为 `GPIO1、GPIO2`。

**现有代码 `extio.begin(&Wire, 2, 1, 0x45)` 是正确的，应保留。** 官方 EXTIO2 [`begin()` 实现第 5-10 行](https://github.com/m5stack/M5Unit-EXTIO2/blob/fcf67c4b16e9b27f9f57ec5ec01ec01efd8e7fec/src/M5_EXTIO2.cpp#L5) 的顺序为 `wire, sda, scl, addr`。本项只需要修正文案；不要交换代码里的 2/1。

## 复现与验收计划（尚未执行）

1. 人工检查三语数字输入代码的模式写入，确认不存在 Pin0 输出 / Pin1 输入组合；该检查不需要将两个输出引脚直接相连。
2. 在固定 Arduino 板包、M5Unified/M5GFX 和 EXTIO2 库版本下，分别编译数字输出、数字输入、SERVO 三段完整例程，记录原有格式类型诊断以及修改后的结果。
3. 用修正后的数字输入例程进行 Pin0→Pin1 回环，连续观察高/低两种状态。保存 `EXTIO2_LOOPBACK out=... in=...`，应在每个稳定状态读到匹配值。
4. 分别运行数字输出与 SERVO 例程，确认固件版本字段正常显示，修正打印方式没有遮蔽对应主要功能。
5. 校对三语渲染页面：正文为 SDA2/SCL1，代码仍为 `begin(&Wire,2,1,0x45)`，数字输入接线、方向和效果说明一致。

## 验收清单

- [ ] 三语数字输入例程分别配置输入/输出，取消该实验中的全通道覆盖逻辑。
- [ ] 三语共 9 处 `%s`/String 参数不匹配全部修正。
- [ ] 三语第 27 行引脚文案统一为 SDA2/SCL1，保留现有正确初始化顺序。
- [ ] 固定依赖版本编译三个受影响的完整例程，保存编译输出。
- [ ] hardware validation 或经过验证、可运行同一 EXT.IO2 协议路径的 virtual-device validation：至少证明模式写入、Pin0/Pin1 高低状态、屏幕字段及 I2C 应答。
- [ ] 保存固件 SHA-256、依赖版本、I2C 参数、协议/串口标记和画面证据；未执行项目继续标记 NOT RUN。
- [ ] 不把替代虚拟设备的结果描述为真实硬件电气测量。
