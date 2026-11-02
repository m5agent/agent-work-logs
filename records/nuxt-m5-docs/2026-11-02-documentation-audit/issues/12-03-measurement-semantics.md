# [文档审查跟踪] 修正 INA226、DoF10 与 AIN4-20mA 示例的测量结果来源、更新标志和单位语义

> 发布边界：本记录按用户针对本次文档工单明确批准的 REVIEW 例外发布。hardware validation 与 virtual-device validation 均为 NOT RUN。公开页面链接可能更新，源文件位置以所列提交、路径和行号为准。

## 审查基线与任务边界

- 文档仓库基线：`47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac`。
- 类型：Arduino / 用户 Example；重点为用户正常采样和读取数据时的正确性。
- 本 issue 为四个可独立审核、实现及关闭的任务，不要求将它们绑定为一个 PR。如维护者偏好独立 issue，可按 A/B/C/D 原样拆分。
- 已完成：文档完整代码与固定版本官方库的控制流、API 语义交叉核对。
- hardware validation：**NOT RUN**。
- virtual-device validation：**NOT RUN**。
- 下述症状由源码路径推导；本文不声称已完成硬件测量或设备运行复现。

## A. INA226 单次测量结果被忽略，打印周期缓存

### 位置

| 语言 | 文件 | 基线行 |
| --- | --- | --- |
| 中文 | `static/zh_CN/arduino/projects/unit/unit_ina226_1a_10a.md` | 123-127 |
| 英文 | `static/en/arduino/projects/unit/unit_ina226_1a_10a.md` | 123-127 |
| 日文 | `static/ja/arduino/projects/unit/unit_ina226_1a_10a.md` | 113-117 |

当前代码执行 `measureSingleshot(d)` 后，打印 `unit_ina226.current()/shuntVoltage()/voltage()/power()`，没有使用输出参数 `d`。

### 独立源码依据

官方 M5Unit-METER 固定版本 `beb6bd90a0f164790dfccbc200834140820d262b`：

- [`unit_INA226.cpp:407-435`](https://github.com/m5stack/M5Unit-METER/blob/beb6bd90a0f164790dfccbc200834140820d262b/src/unit/unit_INA226.cpp#L407)：单次测量读取到传入的 `data`，没有向周期缓存压入该样本。
- [`unit_INA226.hpp:194-215`](https://github.com/m5stack/M5Unit-METER/blob/beb6bd90a0f164790dfccbc200834140820d262b/src/unit/unit_INA226.hpp#L194)：设备对象 `current()` 等读取 `oldest()` 周期数据；缓存为空时返回 NaN。
- [`PlotToSerial.cpp:123-126`](https://github.com/m5stack/M5Unit-METER/blob/beb6bd90a0f164790dfccbc200834140820d262b/examples/UnitUnified/UnitINA226/PlotToSerial/main/PlotToSerial.cpp#L123)：官方例程使用 `d.current()/d.voltage()` 等。
- [`unit_INA226.hpp:90-109`](https://github.com/m5stack/M5Unit-METER/blob/beb6bd90a0f164790dfccbc200834140820d262b/src/unit/unit_INA226.hpp#L90)：结果单位分别为 mV、mV、mW、mA。

### 影响与最小修改

用户停止周期测量、改变负载并完成一次单次采样后，当前输出仍可能是旧的周期数据，不能表示刚完成的单次采样。

仅将成功分支改为从 `d` 读取，并明确单位：

```cpp
Data d{};
unit_ina226.stopPeriodicMeasurement();
if (unit_ina226.measureSingleshot(d)) {
    M5.Log.printf("Single:I=%.2f mA SV=%.3f mV BV=%.1f mV P=%.2f mW\n",
                  d.current(), d.shuntVoltage(), d.voltage(), d.power());
}
```

保留原有测量模式切换流程，不必为了本项重写整个示例。

### 正常复现与验收（尚未执行）

1. 按教程搭建 Core2 + INA226，固定 1A/10A 型号及相应配置，用稳定直流负载开始周期采样。
2. 切换至停止周期的单次模式前后改变负载，在测试副本中同时打印 `d.*` 与 `unit_ina226.*`，记录同一次调用返回的两个来源；不能只观察“命令成功”。
3. 修正后只使用 `d.*` 作为 `Single` 输出。对至少两个稳定负载验证单次结果能随负载变化。
4. 保存固件哈希、库版本、型号配置、模式事件及采样日志；不将未校准的器件读数称为计量精度验证。

- [ ] A：三语示例统一从单次输出参数读取数据。
- [ ] A：打印单位与 API 的 mA/mV/mW 一致。
- [ ] A：固定依赖编译与设备路径运行证据齐全。

## B. DoF10 将标准海平面气压参考高度称为“相对高度”

### 位置与独立依据

三语 `static/{zh_CN,en,ja}/arduino/projects/unit/unit_dof10.md:188` 都打印 `Relative altitude` 却调用 `dof10.baro().altitude()`；第 204 行屏幕也使用同一结果。中文第 19、223 行还把它解释为相对高度。

官方 M5Unit-ENV 固定版本 `5f7d5ef05098d02d5cb56d4b16c2c69cacd9c92c`：

- [`unit_SPA06.hpp:110-119`](https://github.com/m5stack/M5Unit-ENV/blob/5f7d5ef05098d02d5cb56d4b16c2c69cacd9c92c/src/unit/unit_SPA06.hpp#L110)：`altitude()` 默认参考海平面气压 101325 Pa；真正的相对高度接口是 `setAltitudeReference()` + `relativeAltitude()`。
- [`unit_SPA06.cpp:540-552`](https://github.com/m5stack/M5Unit-ENV/blob/5f7d5ef05098d02d5cb56d4b16c2c69cacd9c92c/src/unit/unit_SPA06.cpp#L540)：两个接口分别使用海平面参考与设置的参考点。
- [`barometric_math.hpp:19-26`](https://github.com/m5stack/M5Unit-ENV/blob/5f7d5ef05098d02d5cb56d4b16c2c69cacd9c92c/src/utility/barometric_math.hpp#L19)：所用气压高度公式及默认参考值明确。

### 最小修改选择

推荐最小修正：保留 `altitude()`，将中英日正文和串口/界面标签改为“基于 1013.25 hPa 标准参考气压的气压高度”，避免让用户期待开机位置为零，也避免宣称它等同真实地理海拔。

```cpp
Serial.printf("Pressure altitude (1013.25 hPa): %.2f m\n",
              dof10.baro().altitude());
```

若维护者希望教程目标确实为相对位移，则需要在首个有效气压样本到达后执行 `setAltitudeReference()`，随后显示 `relativeAltitude()`，并把归零时点和方法写入正文。不要在还没有有效样本时归零。

```cpp
// 在首个有效气压样本到达后执行一次：
dof10.baro().setAltitudeReference();
// 后续显示：
const float relative_m = dof10.baro().relativeAltitude();
```

### 正常复现与验收（尚未执行）

1. 在静止位置启动原例程，记录首个有效气压及标为 Relative 的高度；与同一气压代入默认参考公式的结果对比。
2. 若采用标签修正，确认三语均准确说明 1013.25 hPa 参考及其限制。
3. 若采用真正相对高度方案，在固定位置完成归零后确认读数接近零，再移动到另一高度并观察相对变化；记录参考建立事件和原始气压。该检查不等同高度精度标定。

- [ ] B：明确选择气压高度或相对高度这一种教学目标。
- [ ] B：API 调用、屏幕标签、串口标签与三语正文一致。
- [ ] B：相对方案仅在有效样本后归零，并有运行证据；或标准参考方案有公式/读数对应证据。

## C. DoF10 在 500 ms 节流之后检查瞬时 updated 标志，会漏掉串口环境数据

### 位置与独立依据

三语 DoF10 示例：

- 第 151-159 行：每一轮 `units.update()` 后，如果不足 500 ms 就直接返回。
- 第 184-188 行：只有第 500 ms 输出那一轮 `baro().updated()` 为 true 时，才打印气压和温度。
- 中文第 223 行：宣称每 500 ms 同步更新相应数据。

同一官方 M5Unit-ENV 固定版本：

- [`unit_SPA06.cpp:132-145`](https://github.com/m5stack/M5Unit-ENV/blob/5f7d5ef05098d02d5cb56d4b16c2c69cacd9c92c/src/unit/unit_SPA06.cpp#L132)：每次 `update()` 开头都 `_updated=false`，只有本轮实际采样才置 true。它不表示“自上次打印后曾更新”。
- [`unit_SPA06.hpp:34-44`](https://github.com/m5stack/M5Unit-ENV/blob/5f7d5ef05098d02d5cb56d4b16c2c69cacd9c92c/src/unit/unit_SPA06.hpp#L34)：默认 16 次/秒。
- [`unit_SPA06.cpp:32-33`](https://github.com/m5stack/M5Unit-ENV/blob/5f7d5ef05098d02d5cb56d4b16c2c69cacd9c92c/src/unit/unit_SPA06.cpp#L32)：对应轮询间隔约 62 ms。

因此两次打印之间完成的采样标记会在后续轮询中被清掉，除非采样恰好落在打印那一轮，否则不进入环境数据打印分支。具体漏报频率依赖实际调度，**尚未实测，不应预填固定频率或“必然完全不输出”**。

### 最小修改方案

把“是否已有有效样本”和“本轮是否恰好更新”分开处理。若教程目标是每 500 ms 显示最近有效值，最小方案是在节流前记录有效性，节流后读取已缓存的最新气压与温度：

```cpp
// 放在 loop 中 units.update() 后、500 ms 节流之前：
static bool have_baro_sample = false;
if (dof10.baro().updated()) {
    have_baro_sample = true;
}

// 保留现有 500 ms 节流；输出分支改为：
if (have_baro_sample) {
    Serial.printf("Pressure: %.2f hPa\n", dof10.baro().pressure() / 100.0f);
    Serial.printf("Temperature: %.2f C\n", dof10.baro().temperature());
}
```

如果目标是“有新数据时才输出”，则在节流前锁存 `baro_dirty`，在实际输出后清除。两种方案任选其一，正文要对应说明；不要只把 `updated()` 移进另一个同样会漏检查的分支。

### 正常复现与验收（尚未执行）

1. 在测试副本中分别统计驱动 `updated()` 的成功次数与 500 ms 环境输出次数，并打印采样/输出时间戳。
2. 连续记录原例程，再运行同依赖、同配置的修正例程。比较输出节奏，确认温度与气压不再依赖采样/打印恰好同轮。
3. 首个有效样本前不显示无效气压，首个样本后输出周期符合教程约定；失去新数据时应明确区分最近缓存与当前新样本。

- [ ] C：三语代码均在节流前正确消费或锁存更新状态。
- [ ] C：正文中的采样频率、显示频率和输出语义分开说明。
- [ ] C：保存时间戳/计数日志验证修正，具体频率不由静态阅读臆测。

## D. AIN4-20mA 的 mA 显示和 ADC 原始计数缩放矛盾

### 位置与独立依据

三语 `static/{zh_CN,en,ja}/arduino/projects/unit/unit_ain4_20ma.md:51-53`：

```cpp
// 同一个 API 返回值在两个都标 mA 的字段中相差 100 倍：
M5.Display.printf("Current:%.2fmA\r\n", (float)(meter.getCurrentValue(0)) / 100.0);
M5.Display.printf("ADC_Value:%.2f\r\n", (float)(meter.getADC12BitsValue(0)) / 100.0);
M5.Display.printf("Cal_Current:%.2fmA", (float)(meter.getCurrentValue(0)));
```

官方 M5Module-4-20mA 固定版本 `fc17bc5f8f1a6403db7972713ce0968150954a49`：

- [`MODULE_4_20MA.cpp:49-64`](https://github.com/m5stack/M5Module-4-20mA/blob/fc17bc5f8f1a6403db7972713ce0968150954a49/src/MODULE_4_20MA.cpp#L49)：两个 API 分别直接返回 ADC/电流寄存器的整数值。
- [`UnitAIN4-20mA.ino:34`](https://github.com/m5stack/M5Module-4-20mA/blob/fc17bc5f8f1a6403db7972713ce0968150954a49/examples/UnitAIN4-20mA/UnitAIN4-20mA.ino#L34)：官方电流显示把 `getCurrentValue()` 除以 100 转成 mA。
- 当前教程的 `Cal_Current` 并未调用单独的“校准后电流读取”API，读的仍然是同一个 `getCurrentValue(0)`；不能把它解读成已确认存在的第二种 mA 测量。

### 最小修改方案

显示一次电流、一次原始 ADC 计数，删除含义不明且单位错误的重复 `Cal_Current`；若要保留原始电流寄存器，应明确标 `Current raw (0.01 mA/LSB)`，不要再直接标 mA。

```cpp
const uint16_t current_raw = meter.getCurrentValue(0);
const uint16_t adc_raw = meter.getADC12BitsValue(0);
M5.Display.printf("Current: %.2f mA\n", current_raw / 100.0f);
M5.Display.printf("ADC raw: %u\n", static_cast<unsigned>(adc_raw));
```

### 正常复现与验收（尚未执行）

1. 使用固定电流源或已知稳定的传感器输出，原例程同时记录两个标 mA 的字段及原始电流寄存器值，确认相差 100 倍这一显示关系。
2. 修正后分别在两个输入电流水平检查 `Current = raw / 100`、ADC 作为整数计数显示；实际输入值应由适用的校验设备确认。
3. 若没有校验设备，只能声明“单位换算/字段语义验证”，不能宣称电流测量精度已验证。

- [ ] D：三语电流换算一致，删除或明确解释 Cal_Current。
- [ ] D：ADC 原始计数不再无依据除以 100。
- [ ] D：保存原始寄存器值、显示值与换算关系的运行证据。

## 统一交付要求

- [ ] 四个任务分别勾选完成及验证状态，可独立拆分 PR 或 issue。
- [ ] 每个修改的完整例程在记录的依赖版本下编译通过。
- [ ] 每项通过同一实现路径的 hardware validation 或经过验证的 virtual-device validation；未覆盖项目保持 NOT RUN/PARTIAL。
- [ ] 记录固件 SHA-256、运行配置、输入条件、原始数据、串口标记和必要画面；不得把虚拟结果称为物理测量。
- [ ] 中英日三语同步修改代码与正文，不只修中文代码块。
