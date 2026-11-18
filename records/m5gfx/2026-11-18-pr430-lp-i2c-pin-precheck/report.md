# M5GFX PR #430 评审报告：LP I2C 引脚在接受前先拒绝

## 1. 背景与目标

M5GFX 的 `i2c::init()` 在 LP（低功耗）I2C 端口上会先把焊盘借到普通 GPIO、做一次总线清理，
再交给 ESP-IDF 的 `i2c_new_master_bus()`。ESP-IDF 的 LP I2C 驱动只接受 LP IO 引脚，并且在
没有 LP GPIO 矩阵的芯片（ESP32-C5 / C6）上只接受固定的一对
`LP_I2C_SDA_IOMUX_PAD` / `LP_I2C_SCL_IOMUX_PAD`。旧流程在驱动检查之前就改动了焊盘，驱动拒绝后
其失败路径又把焊盘切回 HP 侧，于是这些引脚此前的路由（HP 或 LP，例如被另一个外设占用）丢失。

PR #430 在 `init()` 里先判断引脚是否会被驱动接受，不接受就直接返回 `invalid_arg`，不再触碰
焊盘。这是 #428（让 `i2c_stop()` 的释放动作作用到 LP 焊盘）的后续。

评审目标：确认新判断与驱动规则一致、确认它确实发生在第一次焊盘访问之前、并明确哪些结论只有
代码层证据。

## 2. 变更内容

1 file, +19/-4，`src/lgfx/v1/platforms/esp32/common.inl`：

- 新增 `lp_pads_accepted(sda, scl)`（`:1867-1875`）：`rtc_gpio_is_valid_gpio()` 两脚都通过后，
  在没有 LP GPIO 矩阵且宏存在时要求等于固定对。
- `init()` 的 LP 分支开头新增提前返回（`:2338-2341`），并删去旧注释里「其他引脚交给
  `i2c_stop()` 备份处理」的说法（`:2342-2344`）。

## 3. 代码事实与 ESP-IDF 对照

### 3.1 谓词

ESP-IDF 的 `s_lp_i2c_pins_config()` 顺序是：

1. `ESP_RETURN_ON_ERROR(!rtc_gpio_is_valid_gpio(sda))`
2. `ESP_RETURN_ON_ERROR(!rtc_gpio_is_valid_gpio(scl))`
3. `#if !SOC_LP_GPIO_MATRIX_SUPPORTED` 下要求 SDA / SCL 分别等于
   `LP_I2C_SDA_IOMUX_PAD` / `LP_I2C_SCL_IOMUX_PAD`

四个版本的位置：

| ESP-IDF | 文件 | 行 |
| --- | --- | --- |
| v5.4.4 | `components/esp_driver_i2c/i2c_common.c` | 366-386 |
| v5.5.4 | 同上 | 367-387 |
| v6.0.3 | 同上 | 358-378 |
| v6.1.1 | 同上 | 358-378 |

`lp_pads_accepted()` 的判定顺序与这三点一一对应。`rtc_gpio_is_valid_gpio()` 在 v5.5.4 是
`rtc_io_num_map[gpio_num] >= 0`（`components/esp_driver_gpio/src/rtc_io.c:29-36`），不是简单的
范围判断，所以后面按芯片核对了逐脚映射。

### 3.2 宏守卫的等价性

`LGFX_LP_I2C_LEND_PADS` 的定义条件是

```c
LGFX_LP_I2C_NUM > 0 && SOC_RTCIO_INPUT_OUTPUT_SUPPORTED
&& (!(SOC_LP_GPIO_MATRIX_SUPPORTED) || defined(LGFX_LP_GPIO_MATRIX))
```

而 `LGFX_LP_GPIO_MATRIX` 只在 `SOC_LP_GPIO_MATRIX_SUPPORTED && __has_include(<driver/lp_io.h>)`
时自动定义（`:192-196`）。因此在 P4 上：

- 有 `driver/lp_io.h` → 宏定义，谓词跳过固定对检查，与驱动的 `SOC_LP_GPIO_MATRIX_SUPPORTED`
  分支一致；
- 没有该头文件 → `LGFX_LP_GPIO_MATRIX` 未定义，同时 `LGFX_LP_I2C_LEND_PADS` 也不定义，
  整个谓词不参与编译，不会出现「M5GFX 用固定对规则拒绝 P4 引脚」的错误。

C5 / C6 上 `SOC_LP_GPIO_MATRIX_SUPPORTED` 未定义，`LGFX_LP_GPIO_MATRIX` 也不会被定义，固定对
检查必然参与编译。结论：在 LEND_PADS 生效的所有目标上，`!defined(LGFX_LP_GPIO_MATRIX)` 与
驱动的 `!SOC_LP_GPIO_MATRIX_SUPPORTED` 实际等价。

### 3.3 固定对与逐脚有效集合

| 芯片 / 版本 | 固定对 | 有效 LP IO（`rtc_io_num_map` 非 -1） |
| --- | --- | --- |
| C6 v5.4.4 / v5.5.4 / v6.0.3 / v6.1.1 | 6 / 7 | 0-7 |
| C5 v5.4.4 | 6 / 7 | 0-7 |
| C5 v5.5.4 / v6.0.3 / v6.1.1 | 2 / 3 | 0-6（GPIO7 为 -1） |
| P4 v5.5.4 | 无（LP GPIO 矩阵） | 0-15 |

C5 在 5.5 把固定对从 6/7 移到 2/3，同时 GPIO7 不再是 LP IO；谓词直接使用该版本头文件里的宏，
所以两件事会一起生效，不需要 M5GFX 自己维护版本表。

### 3.4 调用位置

`init()` 的顺序是：软 I2C 分支 → 端口 / 引脚范围检查（`:2279-2286`）→ 已初始化则
`release()`（`:2288-2291`）→ foreign 总线判断（`:2301-2333`）→ LP 分支的新检查（`:2341`）→
`release_lp_pad()` / `pinMode()`（`:2345-2348`）→ `i2c_stop()`（`:2351`）→ 驱动初始化。

- 新检查是 LP 分支里第一条会改变焊盘状态的语句，之前只有句柄查询和端口状态判断。
- `init(port, sda, scl)` 先调用 `setPins()`（`:2454-2462`），而 `setPins()` 会先 `release()`
  旧端口；因此进入 `init(port)` 时 `initialized` 为 false，不会出现「先拆掉旧总线再拒绝新引脚」
  的额外语义。
- 被拒绝时函数直接返回，未写入 `i2c_context` 的 `i2c_bus_handle` / `initialized`，也没有触碰
  焊盘或调用驱动。

## 4. host 判定表

把 `lp_pads_accepted()` 原样抽出（`evidence/host-predicate/predicate.inc`），用一个返回
「该芯片真实 LP IO 集合」的桩替代 `rtc_gpio_is_valid_gpio()`，固定对宏取对应版本 `i2c_ll.h` 的
真实值，用 `clang++ -Wall -Wextra -Werror` 编译执行。5 组配置全部 PASS：

| 配置 | 接受 | 拒绝 |
| --- | --- | --- |
| C6（6/7） | 6/7 | 7/6、4/5、6/5、18/19 |
| C5 5.4（6/7） | 6/7 | 7/6、4/5、6/5、18/19 |
| C5 5.5（2/3） | 2/3 | 6/7、6/5、18/19 |
| P4（矩阵） | 11/9、0/15 | 18/19、11/19 |
| 无固定对宏的旧 SDK | 4/5 | 18/19 |

最后一组说明边界：没有 `LP_I2C_*_IOMUX_PAD` 时只剩 LP IO 有效性检查，有效但非法的引脚会继续
走到驱动并落入旧失败路径；这是旧行为，不是本 PR 引入的回归。

## 5. 影响面与兼容性

- 只影响 LP I2C 端口；HP 端口、软 I2C 端口路径不变。
- 被驱动拒绝的引脚组合从「先动焊盘、驱动报错、再切回 HP」变为「立即 `invalid_arg`」；返回值
  不变，副作用减少。
- 由于不再调用 `i2c_new_master_bus()`，驱动原本会打印的
  `LP I2C SDA/SCL GPIO invalid` 或固定对错误日志不再出现。M5GFX 该文件本来不使用 `ESP_LOG`
  （只有注释），所以没有新增日志，调用方拿到的仍是 `error_t::invalid_arg`。
- 合法引脚组合的行为与 #428 之后完全一致。
- `lp_pads`（`:2363`）在 LEND_PADS 生效时已恒为 true，可保留作防御或删除，不影响正确性。

## 6. 复现命令

```bash
# host 判定表
cd evidence/host-predicate
clang++ -std=c++17 -Wall -Wextra -Werror \
  -DLP_I2C_SDA_IOMUX_PAD=6 -DLP_I2C_SCL_IOMUX_PAD=7 harness.cpp -o c6 && ./c6
clang++ -std=c++17 -Wall -Wextra -Werror \
  -DLP_I2C_SDA_IOMUX_PAD=2 -DLP_I2C_SCL_IOMUX_PAD=3 harness.cpp -o c5 && ./c5
clang++ -std=c++17 -Wall -Wextra -Werror -DLGFX_LP_GPIO_MATRIX harness.cpp -o p4 && ./p4

# ESP-IDF 原文（评审时从公开 tag 获取）
# https://raw.githubusercontent.com/espressif/esp-idf/v5.5.4/components/esp_driver_i2c/i2c_common.c
```

## 7. 未覆盖项、风险与回滚

- **hardware validation：`NOT RUN`**。没有 C5 / C6 实机。作者在 P4 上验证了 GPIO11/9 可用、
  GPIO18/19 返回 `invalid_arg` 且内部总线仍工作；这是引用，不是本记录的复现。
- **virtual-device validation：`NOT RUN`**。没有 C5 profile；C6（QEMU）与 P4（esp-emu native）
  profile 存在，但本变更的差异是「焊盘路由是否被改动」，不是返回值。本地 esp-emulator 检出中
  没有 LP I2C 控制器 / LP IO 路由模型，固件只能读到与改动前相同的 `invalid_arg`，无法区分新旧
  实现。因此没有为了形式去跑一次不可观测的固件。
- **build：`NOT RUN`**。本机没有 Arduino / PlatformIO，也没有可用的本地 ESP-IDF 工具链；
  PR 的 26 项 CI（含 c5 5.5.2、c6 5.4.3、p4 5.4.3、pioarduino c5/c6/p4）全部 pass，仅能证明
  可编译。
- 固定对拒绝路径的运行时行为：`NOT RUN`（作者也未在 C5 / C6 上运行）。已在回复中请作者补一次
  「有效但非固定对被拒绝后，其 IO MUX 路由 / 电平不变」的对照。
- 风险：判断依赖版本头文件里的 `LP_I2C_*_IOMUX_PAD`；若某个 SDK 未定义这些宏，固定对检查
  静默退化，行为回到本 PR 之前。IDF 5.4.3 及以上、Arduino-ESP32 3.1.3 / 3.3.0 均有定义。
- 回滚：仅一个提交，revert 后恢复旧行为；不涉及状态迁移或持久化数据。

## 8. 时间线

- 2026-11-18T07:19Z PR 创建，作者描述 P4 实测与 CI 结果，明确未在 C5 / C6 实机运行。
- 2026-11-18 评审：读取差分与文件、核对 ESP-IDF 四个版本、执行 host 判定表、检索可用虚拟
  profile 与 LP I2C 模型，发布一条英文评审，保持 OPEN，未 push、未改上游仓库。
