# m5stack/esphome#3 评审报告

## 1. 对象与背景

- PR：`[vl53l1x] Add support for the Unit ToF4M`，作者 `New-Kringster`，base `m5-dev`。
- head：`80e8eb6ca6d3f49b6054ea322383d0730f8c4443`（单个提交，作者 `will-tm`，注明
  `cherry picked from 41c3bbff25cac5a04c96e4820846e9ca94d4574e`）。
- base：`6c84e04afe0985a73c705094f88b4f773ed4b6e9`。
- 正文声称：给 `m5-dev` 带来 upstream 的 `vl53l1x` 组件，Unit ToF4M 为 VL53L1X，已在 CoreS3 上通过 PaHub 测试，
  附 Home Assistant 距离卡片截图。正文没有 YAML、没有串口日志。

该提交是 upstream #13605 的逐字节 cherry-pick，因此本次评审重点不是重新审 upstream 的 ULD 逻辑，而是：

1. 在 `m5-dev`（2026.11.0-dev）上能否构建、配置校验是否成立；
2. 在 CoreS3 虚拟设备 + 本机 ToF4M Unit 模型上，组件能否真正跑通；
3. PR 正文的“已测试”是否可核对。

## 2. 代码身份

`git hash-object` 与 upstream `41c3bbff` 的 GitHub contents SHA 对照：

| 文件 | PR blob | upstream blob |
| --- | --- | --- |
| `sensor.py` | `612ee8640811` | `612ee8640811` |
| `vl53l1x.cpp` | `fa3363d1dbde` | `fa3363d1dbde` |
| `vl53l1x.h` | `8deb1c4274f1` | `8deb1c4274f1` |
| `__init__.py` | `034d6aa187fb` | `034d6aa187fb` |
| `LICENSE.txt` | `2b4ec6d3b4fc` | `2b4ec6d3b4fc` |
| `tests/.../common.yaml` | `40a07aaac883` | `40a07aaac883` |
| `tests/.../test.esp32-idf.yaml` | `f5562bc0ee46` | `f5562bc0ee46` |
| `tests/.../test.esp8266-ard.yaml` | `faa50e143b78` | `faa50e143b78` |

相对当前 `esphome/dev` 的差异（`setup_output_pin`、`setup_check`/`status_comm_check`、i2c 字节助手、
`fv.platform_entries`、`sensor.LENGTH_M`、`esphome/components/const.py` 的 `CONF_TIMING_BUDGET`）都是该提交之后
上游做的重构，不是本 PR 偏离；本 PR 不需要为这些新 API 做适配。diff 只有 `CODEOWNERS` 一行和新增目录，
共 9 文件 732 行。

## 3. 构建与配置

环境：macOS arm64、CPython 3.12.14、PR 工作树以 editable 安装（ESPHome 2026.11.0-dev）、ESP-IDF 5.5.6。

- `script/test_build_components.py -c vl53l1x -t esp32-idf`：1 passed / 0 failed。
- 同上 `-t esp8266-ard`：1 passed / 0 failed。
- CoreS3 最小配置（`m5stack-cores3`、`flash_size: 16MB`、`i2c` SDA=GPIO2/SCL=GPIO1、`vl53l1x` 0x29、
  long/50 ms）`esphome config` 通过并完整编译；`firmware.factory.bin` 308784 字节，
  sha256 `bf1813053a64a0f1dc173d03670fcd7a685e06be7f00b538b5d0f817e470ee6e`。
- 注意：ESPHome 2026.11 在 ESP32-S3 上默认把 logger 放到 USB Serial/JTAG，本机 Device Service 只采集 UART0，
  因此测试配置显式写 `logger.hardware_uart: UART0`，否则只会看到 ROM 输出。这是环境事实，与 PR 无关。

schema 反例（全部按预期拒绝，见 `evidence/03-config-validation.txt`）：

- `address: 0x30` 且无 `enable_pin` → “Address other than 0x29 requires enable_pin…”；
- `distance_mode: medium` + `timing_budget: 15ms` → 列出 medium 支持的 20/33/50/100/200/500 ms；
- 16×16 ROI + `roi_center: 150` → “roi_center must be 199…”；
- 同总线两个 0x31 → “Address 0x31 is used by more than one VL53L1X sensor on this bus”。
- 正例：0x30/0x31 双传感器 + 各自 `enable_pin` 的 `tests/components/vl53l1x/common.yaml` 通过（构建即校验）。

## 4. 虚拟设备

### 4.1 设备与接线

`cores3` profile（QEMU，16 MiB flash，ILI9342C 显示），Unit `tof4m` 挂在 `port-a`（ToF4M 的 Grove 线：
黄=SDA=GPIO2，白=SCL=GPIO1，0x29）。创建会话时用服务返回的冻结 pins，未做端口替换。

### 4.2 未改动的 PR 组件：启动成功、传感器握手失败

固件 `bf181305…`（即上节编译产物，经服务归一化为 `b56dc1b1…`）启动：

```
[I][app:073]: Running through setup()
[E][component:311]: vl53l1x.sensor set Error flag: Boot timeout
[E][component:204]: vl53l1x.sensor was marked as failed
[C][i2c:137]: Found device at address 0x29
[I][app:130]: setup() finished successfully!
```

即：节点正常启动、I2C 扫描确实看到 Unit，但组件在 `wait_for_boot_()` 里等
`FIRMWARE__SYSTEM_STATUS (0x00E5) bit0` 100 ms 未成，`mark_failed`。该轮 Unit 侧 `clear-writes=0`、
`transactions=201`，说明只走了配置前的读，没有进入测距。

### 4.3 模型缺口

本机 VL53L1X 模型（`hw/m5stopwatch/m5_unit_i2c_sensors.c` 的 `US_VL53L1X`）只实现 UIFlow `TOF4MUnit` 用到的路径：

1. `0x00E5` 没有实现，读回 `regs[0][0xE5]` 恒为 0；而 ULD（以及 Pololu `VL53L1X::init`）要求轮询该寄存器 bit0。
2. `SYSTEM_MODE_START (0x0087)` 只处理 `0x40`（连续）与 `0x00`（停），忽略组件使用的 `0x10`（单次）；
   而 `0x0087=0x00` 会清掉 `vl_ready`，所以组件永远等不到 data-ready。
3. `0x005E/0x0061` 的 timing-budget 写入只做观察，不解码，Unit 侧 `timing-budget-ms` 恒为 50。

这三点都不是 PR 的缺陷：组件按 ULD 语义实现，模型是按 M5 参考驱动（连续模式、不轮询 0x00E5）裁出来的。
因此**未改动的固件在虚拟设备上无法验证测距数据面**，只能验证到失败分支。

### 4.4 补齐缺口后：组件数据面

为了确认组件其余路径，测试固件（不是 PR 内容）在两处补桥：

- `on_boot`（priority 800）向 `0x29` 写 `00 E5 01`，预置 boot-complete；
- 100 ms `interval` 重复写 `00 87 40`，替模型补上它不认识的单次启动。

结果（`evidence/06-probe-serial.log`、`07-probe-units-summary.json`）：

- 启动后 Unit 侧 `range-status=9`、`timing-budget-ms=50`、`clear-writes` 随每次结果递增；
- 注入 `distance-mm=1000` 时连续 12 次 `DIST_MM=1000`；
- 通过 Unit Input 改为 2500 后连续 29 次 `DIST_MM=2500`（Unit 侧读回 `distance-mm=2500`）。

这说明组件的配置写入、单次启动、data-ready、15 字节结果读取、首次结果后的 VHV 步骤和距离发布都是通的；
串口按 UART0 采集，画面未用于本结论。固件 `f2d75d07…`（服务归一化 `642fa11f…`）。

**证据等级必须按实际写**：这是 virtual-device validation（CoreS3 + ToF4M 模型），但数据面依赖上述两处总线级补桥，
不是一次“模型原生即可跑通”的 PASS；更不是实机。

## 5. 需要作者补的信息

1. 正文没有 YAML：请给出实际配置（PaHub 的 `tca9548a` channel / `i2c_id`、地址、模式与预算），并附一段启动到
   距离读数的串口日志。当前只有 HA 卡片，无法核对“CoreS3 through a PaHub”。
2. 组件在配置里叫 `vl53l1x`，不是 `m5_unit_tof4m`；如果这是有意保持 upstream 命名，建议在正文点明，避免用户
   按其他 M5 Unit 的 `m5_unit_*` 命名去找。
3. 若是多颗 ToF4M 共用一条总线：Grove 口没有 `enable_pin`，而 schema 要求任何非 0x29 地址都必须有
   `enable_pin`，因此同总线多颗不可重地址；PaHub 分通道可以规避。建议在正文说明支持边界。

## 6. 结论与风险

- 无阻塞性缺陷：代码身份、构建、schema 与组件路径均成立；没有发现需要作者改代码才能合并的问题。
- 未覆盖：实机测距/光学/激光安全、PaHub 实机路径、medium 模式、多传感器重地址、HA 实体呈现。
- 风险低：组件是 upstream 已合并代码；剩余风险集中在“PR 正文的测试声明缺少可核对材料”和模型侧缺口。

## 7. 后续（非本 PR）

本机 VL53L1X 模型建议补 `0x00E5` 与 `0x0087=0x10` 两条路径，并把 timing-budget 写入解码为实际毫秒；
否则任何按 ULD 实现的驱动（包括本 PR 和 Pololu 风格代码）在虚拟设备上都只能走到 `Boot timeout`。
