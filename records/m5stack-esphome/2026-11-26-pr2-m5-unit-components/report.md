# m5stack/esphome#2 评审报告

## 1. 任务背景

PR 为 m5stack 的 ESPHome 分支 `m5-dev` 新增三个组件：

- `m5_unit_ncir2`：M5Stack Unit NCIR2（MLX90614 + STM32，带 RGB LED、蜂鸣器、按键），
  传感器 / binary_sensor / 灯 / 输出（rtttl）/ 开关 / 10 个 number 实体；
- `m5_unit_acssr`：Unit ACSSR 与 DCSSR（同一固件，0x50），继电器 switch + RGB 灯，带掉线重连与状态回写；
- `vl53l1x`：从 upstream `esphome/esphome#13605` cherry-pick，供 Unit ToF4M 使用。

评审目标：确认协议实现、构建与可运行性，指出需要作者处理或确认的问题；只读，不 push、不关闭。

## 2. 结论

未发现阻塞性缺陷。三个组件的寄存器映射与厂商 Arduino 库、两颗 Unit 的内部固件逐项一致；
host 单测 31 项通过；esp32-idf 组件构建通过；PR 正文示例在去掉 `relation` 后可在 S32-S3 / CoreS3 完整编译，
并在 CoreS3 虚拟设备上启动到 `setup() finished successfully!`。

需要作者处理/确认 4 点（详见第 4 节）：

1. 正文示例的 `relation: via` 在本分支 schema 中不存在，`esphome config` 失败；
2. NCIR2 的 YAML 告警/发射率写入未落盘；
3. NCIR2 `setup()` 失败后无恢复路径，与 Unit 固件的 500 ms I2C 启动延迟构成竞态；
4. 次要：buzzer switch 忽略 `restore_mode`；ACSSR 读回的是固件影子寄存器，不是继电器实际状态。

## 3. 执行过程与证据

### 3.1 环境

- macOS arm64；仓库 requirements 安装的 ESPHome `2026.11.0-dev`（CPython 3.13 venv）；
- 交叉编译：esp32-idf，ESP-IDF 5.5.6（工具链由 ESPHome 缓存）；
- 虚拟设备：本机 Device Service 的 `cores3` profile（QEMU，16 MB flash，ILI9342C，无 PaHub/Unit 模型）。

### 3.2 配置校验

PR 正文示例原样（含 `relation: via`）：

```
$ esphome config pr-body-example.yaml
Failed config
esphome: None
  ...
      [relation] is an invalid option for [devices]. Please check the indentation.
      relation: via
```

原因：本分支 `esphome/core/config.py` 的 `DEVICE_SCHEMA` 只有 `id / name / area_id`；
upstream `esphome/dev` 已把 `relation` 改成必填（`CONF_RELATION` + `cv.Required`），`m5-dev` 尚未同步。

去掉三行 `relation` 后：

```
$ esphome config pr-body-example-no-relation.yaml
INFO Configuration is valid!
```

### 3.3 构建

```
$ script/test_build_components.py -c m5_unit_ncir2,m5_unit_acssr,vl53l1x -t esp32-idf
Test Summary: 1 passed, 0 failed
```

```
$ esphome compile pr-body-example-no-relation.yaml        # esp32-s3-devkitc-1
Flash: [=         ]  14.0% (used 256267 bytes from 1835008 bytes)
INFO Successfully compiled program.
```

```
$ esphome compile pr-body-example-cores3.yaml             # m5stack-cores3, logger hardware_uart: UART0
Flash: [          ]   3.2% (used 260823 bytes from 8126464 bytes)
INFO Successfully compiled program.
```

镜像：`firmware.factory.bin` sha256 `df05bb829524901d7d7c538bca4a32225c484f090c0af842fb1b522c790a7d6f`，
`m5-units.bin` sha256 `338791b8df999eb2e1f5bf16afe43fde8662678476a974c1ffa7295c6513be13`。

`esphome compile` 首次使用 `logger: hardware_uart: USB_SERIAL_JTAG`（CoreS3 板级默认）时，
该 QEMU 会话只采集到 ROM 输出；改为 `UART0` 后才拿到 IDF 启动日志与组件日志。这是采集通道问题，不是固件缺陷。

### 3.4 host 单测

```
$ script/cpp_unit_test.py m5_unit_ncir2 m5_unit_acssr vl53l1x
[==========] 31 tests from 8 test suites ran.
[  PASSED  ] 31 tests.
```

### 3.5 评审探针（新增，评审后已从工作树删除，源码见 `evidence/probe_review.cpp`）

`LateUnitAfterFailedSetup`：`absent=true` 时 `setup()` → `is_failed()`；随后让 Unit 上线并调用 `update()` / `loop()`，
`is_failed()` 仍为 true —— 证明没有恢复路径。

`YamlSettingsAreNotSavedToFlash`：设置 `high_alarm` 温度后 `setup()`，`regs[0x22..0x23] == 4000`（写入生效），
`regs[0x80] == 0`（从未发送保存命令）。

两项均通过，即第 4 节第 2、3 点可复现。

### 3.6 虚拟设备启动（cores3，QEMU）

固件烧录成功（`flash_prepared verified`，16 MB），启动日志关键段：

```
I (49) boot: Set actual ota_seq=1 in otadata[0]
[I][app:073]: Running through setup()
[I][i2c:250]: Performing bus recovery
[E][tca9548a:107]: TCA9548A failed
[E][component:204]: tca9548a was marked as failed
[E][component:311]: m5_unit_ncir2 set Error flag: Communication failed
[E][component:204]: m5_unit_ncir2 was marked as failed
[W][component:290]: m5_unit_acssr set Warning flag: Communication failed
[E][component:311]: vl53l1x.sensor set Error flag: Boot timeout
[I][app:130]: setup() finished successfully!
...
[W][m5_unit_acssr:041]: Unit not answering at 0x50; check it is in I2C mode (its LED flashes red at power on)
```

同一个缺失的总线条件下，NCIR2 **永久 FAILED**，ACSSR 只报警告并继续按 10 s 间隔重试 —— 这正是第 4 节第 3 点要讨论的不对称。
画面为全黑，因示例未配置 display 组件，不作为失败证据。

## 4. 发现

### 4.1 正文示例在本分支不可用（需要改示例或同步分支）

见 3.2。建议二选一：把示例改成 `m5-dev` 支持的写法（去掉 `relation`），或先同步 upstream 的 `DEVICE_SCHEMA`。
否则任何人照抄正文都无法启动。

### 4.2 NCIR2 的 YAML 告警/发射率设置不落盘

`M5UnitNCIR2::write_settings_()` 写 `REG_ALARM_*` / `REG_EMISSIVITY`，但从不写 `REG_SAVE_SETTINGS(0x80)`；
只有 number 实体的 `control_setting()` 会延迟 5 s 触发 `save_settings_()`。
而 Unit 固件的 `init_flash_data()` 在启动时从自身 flash 读回告警与蜂鸣器设置。
后果：Unit 掉电/重启后回到旧值，ESP 侧 number 仍显示 YAML 值，两边静默分叉。
建议 `setup()` 写完 YAML 设置后同样发一次保存，或在文档里写明“YAML 值只在 ESP 启动时写入、不写 flash”。

### 4.3 NCIR2 失败后无恢复路径，与 Unit 上电时序构成竞态

- `setup()` 读版本号失败即 `mark_failed()`；失败后组件不再被调度，`update()`/`loop()` 都不会再跑（3.5 已复现）。
- NCIR2 内部固件 `main()`：`init_flash_data()` → `sk6812_init()` → `HAL_Delay(500)` → 读 MLX90614 → `user_i2c_init()` +
  `HAL_I2C_EnableListen_IT()`。即 Unit 上电后约 500 ms 才应答 I2C。
- 本分支 ESP-IDF 固件从复位到 `setup()` 只需约 50 ms（虚拟设备日志：49 ms 已 Loaded app）。
- 因此当 Unit 与主板同时上电（CoreS3 的 Grove 5V 还受 AW9523 控制，作者自己在正文里写了这一点）时，
  NCIR2 首次读很可能是 NACK，组件随即永久失效。
- 同一作者给 ACSSR 写了 10×1 s 重连窗口（正是为了 3 s 才启 I2C 的 ACSSR），NCIR2 却没有对应处理。
- 建议：照 ACSSR 的做法加启动重试，或至少在文档写明 NCIR2 必须先于 ESP 上电。

### 4.4 次要一致性问题

- NCIR2 buzzer switch 在 `setup()` 里直接发布 Unit 的使能状态，忽略 `restore_mode`；ACSSR relay 则尊重 restore_mode。
  两处语义不一致，建议统一或说明。
- ACSSR `update()` 读回的 relay/LED 来自 Unit 固件的影子寄存器（`i2c_slave_update()` 保存主机写入的字节，
  掉电后归零），并不能证明继电器触点真的闭合。正文 "The relay state was read back from the unit instead"
  已在 “Not covered” 里承认无带载测试，建议明确“读回的是寄存器镜像”。

## 5. 代码级核对（与厂商实现对照）

NCIR2（`m5stack/M5Unit-NCIR2`、`m5stack/M5Unit-NCIR2-Internal-FW`）：

- 地址 0x5A；0x00/0x90 温度 int16 0.01 °C；0x10 发射率 uint16；
- 0x20 起两个 int16 告警温度；0x30 起两个 3 字节 RGB；0x40 起每个告警 5 字节（freq2/inter2/duty1）；
- 0x50 freq2/duty1/enable1；0x60 RGB；0x70 按键（固件返回按键 GPIO 电平，组件按 0 = 按下处理，极性未在硬件上复核）；0x80 写 1 保存；0xFE 版本；
- 内部固件对写入长度有要求：发射率 `len == 3`、LED `len == 4`、保存 `len == 2`，组件发送的长度与之一致；
- `set_pwm()` 对 `freq > 10000` 直接返回，而组件 number 允许 20–20000 Hz；>10 kHz 时 Unit 不会发声，
  但这属于 Unit 固件行为，组件侧最多算范围标注问题（可考虑把上限收到 10000 Hz）。

ACSSR（`m5stack/M5Unit-ACSSR`、`m5stack/M5Unit-ACSSR-Internal-FW`）：

- 地址 0x50；relay 0x00（1 字节）、LED 0x10-0x12（3 字节）、version 0xFE、改地址 0x20；
- `initial_control()` 把 relay 置 0、`vTaskDelay(3000)` 后才起 I2C slave，与组件“重连并回写状态”的设计一致；
- 内部固件只在 `rw_reg == OUTDRIVE_REG` 且收到数据时切继电器，组件写 `reg 0x00 + 1 byte` 正好匹配。

vl53l1x：5 个文件与 upstream `41c3bbff` blob sha 完全一致，属未改动 cherry-pick，作者与 CODEOWNERS 保留。

## 6. 未覆盖项与边界

- 没有实体 Unit，也没有 Unit 模型：传感器读数、告警声、LED、继电器带载、Modbus、HA 子设备呈现全部 NOT RUN。
- 虚拟设备只有控制器侧：验证到“缺 Unit 时的失败/重试行为”和“固件能启动”，没有任何 Unit 功能验证。
- `tca9548a`(PaHub) 未在虚拟设备建模，故多总线切换路径未执行。
- 未验证 Unit 内部 flash 的掉电保持（需要真实 Unit 断电）。
- 结论等级：host-level test（31 项 + 2 项探针）、virtual-device validation（仅启动与错误路径）、
  code-level verification（厂商库/固件对照）；无 hardware validation。
