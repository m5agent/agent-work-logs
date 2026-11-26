# m5stack/esphome#4 `[m5_unit_ncir2]` 评审报告

## 1. 条目与范围

- PR：https://github.com/m5stack/esphome/pull/4
- 作者：New-Kringster
- 状态：OPEN、非 draft、无既有评论；本轮为首次回复。
- base：`m5-dev @ 6c84e04afe0985a73c705094f88b4f773ed4b6e9`
- head：`269124e77bbcd2a128f799ed5fcb31e8a1fbc5de`
- 变更：新增 `esphome/components/m5_unit_ncir2/`（hub + sensor + binary_sensor + number + switch + output + light）、
  `tests/components/m5_unit_ncir2/` 与 `CODEOWNERS` 一行；共 23 个文件。

PR 正文称 "Tested on a CoreS3 through a PaHub"，本次评审不复用作者结论，独立取证。

## 2. 与 #2 的关系

PR #2 被作者拆分为 #3（ToF4M）、#4（NCIR2）、#5（ACSSR/DCSSR）。逐 blob 比较：

| 文件 | #2 head (`e8acee5`) | #4 head (`269124e`) |
| --- | --- | --- |
| `m5_unit_ncir2.cpp` | `be9aecd6…` | `be9aecd6…` |
| `m5_unit_ncir2.h` | `371aa997…` | `371aa997…` |
| `__init__.py` | `3cff5081…` | `3cff5081…` |

`git diff e8acee5 269124e -- esphome/components/m5_unit_ncir2 tests/components/m5_unit_ncir2` 为空；
`CODEOWNERS` 仅少了 ToF4M/ACSSR 两行。即 #4 并未修改 NCIR2 实现，因此 #2 中针对 NCIR2 的结论仍适用，
本轮在 #4 head 上重新取证，并补充了新的虚拟设备功能验证。

## 3. 协议与实现核对

对照 `m5stack/M5Unit-NCIR2` 库与 `M5Unit-NCIR2-Internal-FW`：

- 地址 `0x5A`；`0x00/0x90` 为 int16、0.01 °C；`0x10` 发射率 uint16；`0x20` 起两个 int16 告警温度；
  `0x30` 起两个 3 字节 RGB；`0x40` 起每个告警 5 字节（freq2/interval2/duty1）；`0x50` freq2/duty1/enable1；
  `0x60` RGB；`0x70` 按键；`0x80` 写 1 保存；`0xFE` 版本。
- 组件写入长度与内部固件要求一致：发射率总长 3、LED 总长 4、告警 LED 总长 4、蜂鸣器总长 5（0x50 起 4 数据）、
  保存总长 2。
- 告警温度寄存器在 Unit 固件中为 `volatile int16_t`，量纲 0.01 °C，可表示上限 +327.67 °C。

## 4. 执行与证据

### 4.1 host 测试与探针

```
$ script/cpp_unit_test.py m5_unit_ncir2
[==========] 23 tests from 7 test suites ran.
[  PASSED  ] 23 tests.
```

其中 20 项为 PR 自带测试；另 3 项为评审探针（`code/probe_pr4_review.cpp`）：

1. `YamlSettingsAreNotSavedToFlash`：`set_alarm_temperature(1, 4000)` + `setup()` 后 `0x22=4000`，`0x80=0`。
2. `LateUnitAfterFailedSetupStaysFailed`：Unit 缺失时 `setup()` 失败；随后 Unit 上线并调用 `update()`/`loop()`，
   `is_failed()` 仍为 true。
3. `AlarmTemperatureAboveInt16RangeWraps`：`control_setting(HIGH_ALARM_TEMPERATURE, 380.0)` 写出的寄存器为
   `0x9470`，按 int16 解释为 `-27536`（-275.36 °C）。

### 4.2 构建

```
$ script/test_build_components.py -c m5_unit_ncir2 -t esp32-idf
Test Summary: 1 passed, 0 failed
```

完整编译：

- CoreS3 配置（`code/cores3-ncir2.yaml`，board `m5stack-cores3`）：`Successfully compiled program`，
  factory.bin sha256 `ba03930bdc3d990205f9690738e4bcc6bbb31eab14bd1c56c164cf951e9be17b`。
- AtomS3R 测试配置（`code/atoms3r-ncir2-test.yaml`，board `esp32-s3-devkitc-1`、8 MB flash、SDA=GPIO2/SCL=GPIO1）：
  `Successfully compiled program`，factory.bin sha256 `b2f543e8f56371c0981a10a07bef439cd053cc49ee46ff3372cdb293acc99ec4`。

### 4.3 虚拟设备 A：CoreS3，无 Unit（失败路径）

固件 `ba03930b…` 烧录到 `cores3` profile（QEMU，16 MB flash；该镜像头声明 4 MB flash，无 PaHub/Unit 模型）。串口：

```
[I][app:073]: Running through setup()
[I][i2c:250]: Performing bus recovery
[E][component:311]: m5_unit_ncir2 set Error flag: Communication failed
[E][component:204]: m5_unit_ncir2 was marked as failed
[I][app:130]: setup() finished successfully!
...
[E][component:143]:   m5_unit_ncir2 is marked FAILED: Communication failed
```

`setup()` 首次读版本失败即 `mark_failed()`，后续没有任何重试。

### 4.4 虚拟设备 B：AtomS3R + NCIR2 Unit（功能路径）

`atoms3r` profile（QEMU，8 MB flash）挂接 NCIR2 模型于 `custom` 端口（模型准入仅此主机；`cores3` 报
`ncir2 has no controller wiring for cores3`）。固件 `b2f543e8…`。

启动：

```
[C][i2c:111]:   SDA Pin: GPIO2
  SCL Pin: GPIO1
[C][i2c:137]: Found device at address 0x5A
[C][m5_unit_ncir2:187]: M5Stack Unit NCIR2:
  Firmware version: 1
```

通过 `unit-input` 依次注入并观察串口（每 5 s 轮询）：

| 注入 | 串口观测 |
| --- | --- |
| object 32.0 / chip 25.0 | `OBJECT_C=32.00`、`CHIP_C=25.00` |
| object 45.0 | `OBJECT_C=45.00` |
| object -20.5 | `OBJECT_C=-20.50` |
| chip 30.25 | `CHIP_C=30.25` |
| button true | `BUTTON=1` |
| button false | `BUTTON=0` |

执行实体动作并读取 Unit 模型状态：

- `switch.turn_on buzzer` 后 `buzzer-on=true`；`switch.turn_off` 后 `buzzer-on=false`。
- `light.turn_on` 蓝色后 `rgb-led=255`（0x0000FF）。
- 全程 I2C `transactions` 从 341 增至 2957，`written-bytes` 从 394 增至 1929。

这验证了组件的传感器读取、按键轮询、蜂鸣器与 RGB 写入路径；未验证告警自主行为（模型不实现阈值状态机）。

### 4.5 发现

1. **启动失败无恢复（主要）**：`setup()` 在首次 `read_register_(REG_FIRMWARE_VERSION)` 失败即 `mark_failed()`。
   NCIR2 内部固件在 `init_flash_data()` + `sk6812_init()` + `HAL_Delay(500)` + MLX90614 读取之后才
   `HAL_I2C_EnableListen_IT()`；ESP 侧在约 50 ms 就完成 setup。冷启动同 5V 上电时存在竞态。
   Unit 稍后上线不会恢复（探针 2 + CoreS3 串口）。作者给 ACSSR 做了 10×1 s 重连窗口，NCIR2 没有。
2. **YAML 设置不落盘（中等）**：`write_settings_()` 只写 `0x10/0x20/0x30/0x40`，从不写 `0x80`；只有 number
   实体变更后经 `SAVE_DELAY_MS` 才 `save_settings_()`。Unit 单独掉电重启后从自身 flash 恢复旧告警值，
   而 number 实体仍显示 YAML 值，直到 ESP 重启重新写入。
3. **告警温度上限溢出（中等，新发现）**：schema 允许 -70…380 °C，number 上限也是 380，但寄存器是 int16
   0.01 °C；380 °C 编码为 `0x9470`（-275.36 °C）。Device Service 的 NCIR2 模型说明也明确写着
   "signed int16 x0.01 encode limit (+327.67C) … no 380C correctness claim"。
4. **次要**：`set_pwm()` 在 Unit 固件中对 `freq > 10000` 直接返回，而 number/output 允许 20–20000 Hz，
   10–20 kHz 会被接受但不发声；buzzer switch 在 `setup()` 发布 Unit 当前状态，非默认 `restore_mode`
   （如 RESTORE_DEFAULT_ON）不会生效。

## 5. 影响面与回滚

- 纯新增组件，不改既有组件；回滚即删除 `m5_unit_ncir2` 目录与 CODEOWNERS 一行。
- 未 push 上游、未关闭 PR、未修改作者分支。

## 6. 未覆盖项

- 无实体 NCIR2：hardware validation NOT RUN；所有数值来自注入的虚拟 Unit 输入，不是物理测量。
- Unit 模型不实现 STM32 告警状态机，阈值触发、告警灯/告警声 NOT RUN。
- Unit 内部 flash 掉电保持 NOT RUN（模型不暴露寄存器/闪存内容）。
- PaHub（`tca9548a` 未建模）与作者所述 CoreS3+PaHub 拓扑 NOT RUN。
- 光学、发射率物理、实际声压/亮度 NOT RUN。
