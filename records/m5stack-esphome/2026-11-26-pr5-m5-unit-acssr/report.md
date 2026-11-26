# m5stack/esphome#5 Unit ACSSR / DCSSR 组件评审报告

## 1. 目标与背景

PR #5 将原先包含在 #2 中的 ACSSR/DCSSR 部分拆出，新增 `m5_unit_acssr` 组件：
一个 `switch`（继电器）和一个 `light`（RGB LED），挂在同一个 I2C hub 上。
作者说明 Unit DCSSR 与 ACSSR 运行同一套固件，因此一个组件覆盖两款产品；PR 正文
声明已在 CoreS3 + PaHub 上实测。

本轮工作为只读评审：不关闭 PR、不 push、不修改作者仓库，只发一条英文回复
（<https://github.com/m5stack/esphome/pull/5#issuecomment-7181243369>）。

- PR head：`d67c91f656fba5333b5f67d237200c244769342b`
- Base：`m5-dev @ 6c84e04afe0985a73c705094f88b4f773ed4b6e9`
- 变更：13 个文件，+549 行；组件、switch/light 平台、CODEOWNERS、host 测试与
  `test.esp32-idf.yaml`

## 2. 代码核对

### 2.1 寄存器与传输

| 地址/寄存器 | 组件实现 | 厂商库 / Unit 固件 |
| --- | --- | --- |
| 0x50 | `i2c_device_schema(0x50)` | `ACSSR_DEFAULT_ADDR 0x50` |
| 0x00，1 字节 | relay 0/1 | `ACSSR_I2C_RELAY_REG 0x00`，`ctrl_set_op()` |
| 0x10，3 字节 | R/G/B | `ACSSR_I2C_LED_REG 0x10`，3 字节大端 |
| 0xFE，1 字节 | 固件版本 | `ACSSR_I2C_VERSION_REG 0xFE` |

`read_register_()` 采用“先写寄存器地址，再单独读”的两段传输，与厂商库
`M5_ACSSR::readBytes()` 相同；没有使用 ESPHome 的单事务 `read_register()`，
避免依赖 Unit 的 repeated-start 行为。写入路径为 0x00 单字节和 0x10 三字节，
也与 `M5_ACSSR::on()/off()/setLEDColor()` 一致。

### 2.2 上电与重连

Unit 固件 `initial_control()` 先闪灯、`vTaskDelay(3000)`，再把继电器置 0，之后
才 `i2c_slave_init()`（`main/acssr.c:133-154`，`:192`）。组件在 `setup()` 失败后
以 1 s 间隔重试 10 次，然后转为默认 10 s（probe 使用 5 s）的 `update()` 周期继续探测；这与 3 s 上电
窗口一致。

### 2.3 restore_mode 与反转

`setup()` 读取 `get_initial_state_with_restore_mode()`；`DISABLED` 时从 Unit 读
0x00。`relay_on_` 保存的是硬件电平（`logical != inverted`），`publish_state()` 接收
硬件电平并由基类应用反转；测试覆盖了 `ALWAYS_OFF` / `RESTORE_DEFAULT_OFF` /
`DISABLED` / 反转 / 写入失败 / 晚到 Unit / Unit 重启恢复。

### 2.4 重启恢复判据

`update()` 同时读 0x00 和 0x10，与 hub 保存的 `relay_on_`、`led_` 比较；不同就
重写。前提是“I2C 模式下只有 hub 改这两个寄存器”，与 Unit 固件一致：Button/Modbus
模式不会同时运行。读回值是 Unit 的写入影子，不是触点/光学反馈。

## 3. 执行环境与命令

```bash
# 主机单测
script/cpp_unit_test.py m5_unit_acssr

# esp32-idf 组件构建
script/test_build_components.py -c m5_unit_acssr -t esp32-idf

# probe 配置校验与完整编译
python -m esphome config evidence/08-cores3-dcssr-probe.yaml
python -m esphome compile evidence/08-cores3-dcssr-probe.yaml
```

环境：macOS arm64，CPython 3.13 venv，ESPHome 2026.11.0-dev，ESP-IDF 5.5.6。
虚拟设备：本机 Device Service 的 `cores3`（QEMU，16 MB flash），Unit 模型
`dcssr`（与 ACSSR 共用官方 `acssr.py` 寄存器子集），PORT.A（SDA=2，SCL=1）。

## 4. 结果

### 4.1 Host 单测

`11 tests from 2 test suites` 全部通过，覆盖：

- restore mode + inverted
- 断线时写入失败不发布新状态
- Unit 晚上线时 LED 先缓存、上线后写出
- 快速重试耗尽后由 `update()` 接管
- Unit 重启后继电器和 LED 恢复
- 匹配时 `update()` 不额外写

### 4.2 组件构建与配置

- `test_build_components.py`：`1 passed, 0 failed`
- `esphome config`：`Configuration is valid!`；默认 `update_interval: 10s`，
  `address: 0x50`，switch 默认 `restore_mode: ALWAYS_OFF`，light 默认 gamma 2.8

### 4.3 虚拟设备（CoreS3 + DCSSR）

- Session `8b79463b8e1140ea83f4d59dd6723b51`
- 固件：`dc08a5b0c54517c222592b12925f5653b28aa5e08000bd1c0120db7ef45100d8`
  （factory artifact `33255cfcbb3f389e3474c05c5768021ba70c6068b671e820f00442f7a1bae36b`）
- UART0：`setup() finished successfully!`、`Firmware version: 1`、`Turning ON`、
  `Turning OFF`
- QOM 采样：
  - 早期：`relay-level=true`、`relay-transitions=1`、`led-rgb=0xFF8000`
  - 后期：`relay-level=false`、`relay-transitions=2`、`led-rgb=0xFF8000`、
    `fw-version=1`、`i2c-address=0x50`、`transactions=233`、`read-bytes=38`、
    `written-bytes=762`
- 结论：组件确实通过 I2C 把 0x00 和 0x10 写到了 Unit 模型；LED 的最终
  `0xFF8000` 与脚本设置的 RGB(255,128,0) 一致。

### 4.4 无 Unit 会话

- Session `cd1722e88bf84ae282fc29b6435f3c55`
- `setup() finished successfully!`，`Communication failed` 警告，重连窗口结束后
  一条 `Unit not answering at 0x50; check it is in I2C mode (its LED flashes red at
  power on)`；之后仍能看到 0x50 的 `TX FE` 探测，说明 `update()` 没有停止。
- 这验证了失败路径不会 `mark_failed()`，也不会卡死；未验证 Unit 在会话中途出现
  （设备服务不支持运行中热插拔）。

### 4.5 QEMU 模型缺口

QEMU DCSSR 模型的 `snapshot_registers()` 只把 0x00 和 0xFE 写入
`read_snapshot`，没有把 0x10 的 `acssr_led_rgb` 反射回去；因此组件读 0x10 恒为 0，
`update()` 每次都会判定状态丢失并重写，串口出现 8 次
`Unit lost its relay and LED state...` 警告。真实 Unit 固件在
`components/test/i2c_slave.c:75-96` 把除 0xFE 外的写入都保存在 `rw_register_data`，
读回应当匹配。因此这是模型缺口，不是组件缺陷；但它意味着“重启恢复不会误判”
这一条在虚拟设备上无法公平验证。

## 5. 评审意见

未发现阻塞问题。建议作者补充一条实机 Unit 断电重启（或按复位）后的串口日志，
确认 `update()` 只在真正重启后恢复一次，而不是反复告警；同时确认“Unit 离线时
继电器命令被丢弃、LED 设定值被缓存”的语义是否符合预期（现有
`FailedWriteKeepsTheState` 测试已固定该行为）。

## 6. 未覆盖项与风险

- 无实机：继电器触点、AC/DC 带载、隔离、寿命、LED 光学、真实 3 s 上电窗口
  `NOT RUN`；QEMU 只是寄存器/事务模型，不能描述市电开关能力。
- Unit 的 Button 与 Modbus/RS485 模式、0x20 改址未覆盖。
- 继电器读回是影子字节，不是触点反馈；“恢复”只表示寄存器一致。
- 若 Unit 固件版本变化导致 0x10 读回语义变化，`update()` 的判据需要重新核对。
