# m5stack/esphome#3 Unit ToF4M 的 vl53l1x 组件评审

- 日期：`2026-11-26`
- 结果：`REVIEW`
- 工作类型：`pr_review`
- 问题来源：https://github.com/m5stack/esphome/pull/3
- 已发布回复：https://github.com/m5stack/esphome/pull/3#issuecomment-7181290860
- 源码版本：`m5stack/esphome @ 80e8eb6ca6d3f49b6054ea322383d0730f8c4443`（PR head），base `m5-dev @ 6c84e04afe0985a73c705094f88b4f773ed4b6e9`
- 环境：macOS arm64；CPython 3.12 + PR 工作树（ESPHome 2026.11.0-dev）；ESP-IDF 5.5.6；本机 Device Service 的 `cores3` profile（16 MiB flash，带 Unit ToF4M 模型，`port-a`）

## 结论

PR #3 把 upstream `#13605`（`41c3bbff`）原样 cherry-pick 到 `m5-dev`：五个组件文件与三份测试夹具的 blob SHA
完全一致，`m5-dev` 缺的只有这个组件本身。esp32-idf 与 esp8266-ard 组件构建各 1/1 通过，
CoreS3 配置可校验、可完整编译；地址、时序预算、ROI 与同总线重地址的 schema 约束都按设计报错。

在 CoreS3 虚拟设备上挂接 ToF4M Unit 后，固件正常启动，I2C 扫描到 `0x29`。但本机 VL53L1X 模型缺
`FIRMWARE__SYSTEM_STATUS (0x00E5)` 与单次启动（`0x0087=0x10`）两项，组件按 ULD 语义报 `Boot timeout`；
用测试固件在总线上补齐这两项后，组件把 1000 mm 注入值发布为 `1.000 m`，改注入 2500 mm 后连续发布
`2.500 m`，range status 9、clear-writes 递增。因此**组件路径可用，缺口在虚拟设备模型侧**，不是 PR 缺陷。

唯一需要作者补的是可核对证据：正文只有 Home Assistant 卡片截图，没有 YAML 配置与串口日志，也没有说明
该组件暴露为 `vl53l1x` 而不是 `m5_unit_tof4m`。实机、光学/量程、PaHub 与 medium 模式均 NOT RUN。

## 关键证据

- 代码身份：`sensor.py`、`vl53l1x.cpp`、`vl53l1x.h`、`__init__.py`、`LICENSE.txt` 与三份测试 YAML 的 blob SHA
  与 upstream `41c3bbff` 逐项相同（`evidence/01-identity.txt`）；与当前 `esphome/dev` 的差异全部是后续上游重构
  （`i2c` 字节助手、`setup_check`/`status_comm_check`、`fv.platform_entries`、`sensor.LENGTH_M`、`const.py` 常量），
  不是本 PR 的改动。
- 构建：`test_build_components.py -c vl53l1x -t esp32-idf` 与 `-t esp8266-ard` 均 1 passed / 0 failed
  （`evidence/02-component-builds.txt`）；CoreS3 配置（`m5stack-cores3`、16 MB、0x29、long/50 ms）完整编译，
  factory.bin sha256 `bf181305…470ee6e`（`evidence/09-firmware.txt`）。
- schema：非 0x29 且无 `enable_pin`、medium+15 ms、16×16 ROI 配 `roi_center: 150`、同总线重复地址均被拒绝；
  双传感器 0x30/0x31 夹具通过（`evidence/03-config-validation.txt`）。
- 虚拟设备（无绕过）：启动到 `setup() finished successfully!`，总线扫描 `Found device at address 0x29`，
  `vl53l1x was marked as failed: Boot timeout`（163 ms）；`evidence/04-plain-serial.log`。
- 虚拟设备（补齐模型缺口）：`DIST_MM=1000` 连续 12 次，注入改 2500 后 `DIST_MM=2500` 连续 29 次；
  Unit 侧 distance-mm 2500、range-status 9、timing-budget-ms 50、clear-writes 83（`evidence/06`、`evidence/07`）。

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/`：身份、构建、schema、串口与 Unit 状态、测试配置、固件哈希

## 未覆盖项

- 没有物理 ToF4M：实际测距、4 m 量程、分辨率、940 nm 光学与激光安全、上电时序均 NOT RUN。
- 没有实机 PaHub 路径；正文所称 “through a PaHub” 无法复核。
- medium 模式的 timing-budget 表不是 ULD 原表，未做硬件或模型验证，不作结论。
- 多传感器重地址（`enable_pin` + 非 0x29）仅在 host schema 层验证，未在虚拟或实机 I2C 上执行。
- Home Assistant 实体呈现仅见正文截图，未复现。
