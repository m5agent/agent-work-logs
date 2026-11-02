# [文档审查] Chain DualKey 右侧 UART 示例及 24 处教程注释的 RX/TX 映射颠倒

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

## 审查基线与验证状态

- 文档仓库：`nuxt-m5-docs`。
- 文档基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`。
- 问题类型：Arduino / 用户 Example 的引脚映射错误。
- 已完成：逐项核对示例、官方驱动调用顺序及公开原理图原图。
- hardware validation：**NOT RUN**。
- virtual-device validation：**NOT RUN**。
- 本文中的通信失败是由引脚映射与驱动调用路径推导出的预期结果，尚不是设备运行实测结论。建议人工审核后按下述验收方案补齐证据。

## 问题与影响

`static/zh_CN/arduino/projects/chain/chain_bus.md:185-186` 的双接口示例实际配置为：

```cpp
#define RXD_PIN_R GPIO_NUM_47
#define TXD_PIN_R GPIO_NUM_48
```

同一示例的第 193 行将其传给 `M5ChainRight.begin(&Serial2, 115200, RXD_PIN_R, TXD_PIN_R)`。Chain DualKey 的这一路硬件实际连接是 **GPIO48 接收、GPIO47 发送**；当前示例配置相反。用户沿用该配置接入这侧 Chain 设备时，预计无法正常枚举或收发数据。

此外，三语共 24 个教程文件把“换到另一侧”的说明写成 `RX=47、TX=48`。即使默认 `RX=5、TX=6` 示例能够工作，用户按注释换接口时仍会配置错。

## 独立依据

1. [Chain DualKey 公开原理图第 3 页](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1176/Chain_DualKey_SCH_V1.5_20250725_2025_07_25_16_06_51_page_03.png) 左侧 UART 网络明确标注 `GPIO47 → UART1_TX`、`GPIO48 → UART1_RX`；U27 的 pin1 为 TX、pin2 为 RX。该原图已实际打开核对，SHA-256 为 `68d899624de7431af7fb9a7cfe0fd50e4dd530000de8c8e146f6d70e54f6294a`。
2. [M5Chain 固定版本 `277dcfe84a5712ef1bb07299f923360c5482d107` 的 `ChainCommon.cpp:29-33`](https://github.com/m5stack/M5Chain/blob/277dcfe84a5712ef1bb07299f923360c5482d107/src/ChainCommon/ChainCommon.cpp#L29) 把 `rxPin, txPin` 原样传入 `HardwareSerial::begin()`，没有内部交换映射。
3. 文档仓库同一基线的 `static/zh_CN/chain/Chain_DualKey.md:139-145` 产品引脚表也分别给出 `G48=UART1_RX、G47=UART1_TX` 和 `G5=UART2_RX、G6=UART2_TX`。这是仓库内一致性依据，独立硬件依据仍为上述原理图。

## 受影响范围

| 范围 | 基线位置 | 修改内容 |
| --- | --- | --- |
| 中文实际双接口示例 | `static/zh_CN/arduino/projects/chain/chain_bus.md:185-186` | 交换右侧 RX/TX 常量 |
| 中文通用总线教程注释 | `static/zh_CN/arduino/projects/chain/chain_bus.md:51-52` | 另一侧改为 RX48/TX47 |
| 英文及日文通用总线教程注释 | `static/{en,ja}/arduino/projects/chain/chain_bus.md:39-40` | 同步更正 |
| 三语产品教程注释 | `static/{zh_CN,en,ja}/arduino/projects/chain/chain_{angle,encoder,key,joystick,tof,buzzer,switch}.md` | 同步更正另一侧引脚 |

`angle/encoder/key/joystick/tof` 的错误注释从第 25 行开始；`buzzer/switch` 从第 26 行开始。路径花括号表示逐个文件展开，不是实际文件名。

`chain_mic.md:25-26` 三语注释已经是 **RX48/TX47**，应保留。当前英文/日文 `chain_bus.md` 未找到中文同款双接口代码块，不应把该实际代码错误声称为三语都存在；但三语的另一侧注释都需要修正。

## 最小修改方案

把中文双接口示例改为：

```cpp
// Right side of Chain DualKey: GPIO48 RX, GPIO47 TX.
#define RXD_PIN_R GPIO_NUM_48
#define TXD_PIN_R GPIO_NUM_47
```

把所有受影响的另一侧注释统一为：

```cpp
#define RXD_PIN GPIO_NUM_5  // 48 for the other side of Chain DualKey
#define TXD_PIN GPIO_NUM_6  // 47 for the other side of Chain DualKey
```

默认一侧的数值 5/6、UART 波特率及协议逻辑保持现有配置。补一张明确“主控 RX/TX”视角的接口表，避免用户把模块端 TX/RX 或左右外观视角混入主控引脚定义。

## 正常使用复现与验证方案（尚未执行）

1. 使用 Chain DualKey、一个已知正常的 Chain 输入设备以及正确方向的 Bridge/Return 连接器；记录实际板卡版本、M5Chain 固定版本及 Arduino 板包版本。
2. 用 `chain_mic` 或对应产品的完整枚举例程，在默认 GPIO5 RX / GPIO6 TX 一侧确认设备能够被发现。保存枚举状态码、数量和设备类型作为基准。
3. 将同一设备移到 GPIO47/48 对应接口，只修改 RX/TX 为当前错误注释所写的 RX47/TX48；记录枚举结果。本步骤的失败是预期，不能在未执行前填写“已复现”。
4. 将 RX/TX 更正为 RX48/TX47，重新构建上传，并重复同样的枚举和数据读取。
5. 如需验证中文双接口示例，在两侧各连接一个已知正常设备，分别打印每个 Chain 实例的枚举结果。原示例 `loop()` 为空，本身不产生枚举证据，因此应补入显式探测代码，不能用“上传成功”作为验证通过。

可在右侧实例初始化后执行以下探测；`Serial.begin(115200)` 需要在 `setup()` 中初始化：

```cpp
uint16_t count = 0;
const auto status = M5ChainRight.getDeviceNum(&count);
Serial.printf("CHAIN_RIGHT status=%u count=%u\n",
              static_cast<unsigned>(status), static_cast<unsigned>(count));
```

## 验收清单

- [ ] 人工逐项核对原理图与主控 RX/TX 方向。
- [ ] 中文实际双接口代码更正为 RX48/TX47。
- [ ] 三语 24 个受影响教程文件的另一侧注释全部同步。
- [ ] `chain_mic` 已正确的注释保持正确。
- [ ] 固定依赖版本编译修改后的完整例程。
- [ ] hardware validation 或能真实运行相同 UART 路径的 virtual-device validation：默认侧、另一侧、双侧枚举及至少一项有效数据读取均有日志。
- [ ] 记录固件 SHA-256、UART 配置、枚举状态码/数量/类型和应用读取结果；不包含设备唯一标识或内部地址。
- [ ] 将构建、运行验证和未覆盖内容分开报告，不能以编译上传成功替代通信验证。
