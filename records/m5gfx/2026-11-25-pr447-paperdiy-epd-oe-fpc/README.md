# M5GFX #447: PaperDIY EPD OE no longer driven from G45; FPC connectors replace the Grove port

- 日期：`2026-11-25`
- 结果：`PASS`（无阻塞问题；证据等级 virtual-device validation + code-level verification；
  真机 `NOT RUN`；仅一处非阻塞的 provenance 注解建议）
- 工作类型：`pr-review`
- 条目：[m5stack/M5GFX#447](https://github.com/m5stack/M5GFX/pull/447)，作者 ainyan03，
  英文，OPEN，非 draft；评审前 comments / reviews 均为 0，m5agent 未回复过
- 源码：`m5stack/M5GFX` PR head `a5fdf82cae2ebf3385f622302a1ffe917b197fdc`
  （base `develop` `72001da0fdd7232a8a8ac77cd84120801f879496`）
- 配套条目：`m5stack/M5Unified#451` head `bf06bc4ef325a2776d23348c08f3bb6976a59e5c`
- 改动范围：7 文件 `+203/-30`，含 catalog、connector type、生成物、host 测试与一个生成头文件
- 环境：macOS 26.5.1 arm64，Node v26.13.1，ESP-IDF v6.1（esp32s3），
  Device Service `paperdiy` profile（partial，ET047TC1 540x960，16 MiB flash / 8 MiB PSRAM）

## 结论

无阻塞问题，可与 M5Unified#451 一起合入。

- K159-B 原理图第 4 页中，面板连接器 pin 12 `XOE` 与 pin 7 `VDD`、pin 23 `TEST` 同属
  `EPD_PWR` 网络；G45 只出现在 FPC-I2S 的 `MCLK` 网络。官方 PinMap 的 12+12 个 FPC 端子
  与 PR 的 `fpc_i2s` / `fpc_spi` 目录逐项一致，`3v3_au` 导轨和 `pin:pmic.gpio*` 也对得上。
- `display_oe = -1` 在库里是安全值：`Bus_EPD` 只把 `pin_oe` 交给 `gpio_hi/gpio_lo`
  与 `pinMode`；前两者对负引脚直接跳过，`pinMode` 对 `(size_t)pin >= GPIO_NUM_MAX` 提前返回。
  EPD_PWR 已由 PMIC GPIO2 在板级上电流程中打开，去掉 OE 驱动不会漏掉电源时序。
- 生成物可从 catalog 逐字节重建；`node cli/spec.js check` 通过，`npm test` 221/221 通过；
  与 M5Unified#451 的 `compare-pintable` 55 板 / 2750 值全部一致。
- A/B 虚拟设备对照：base（`display_oe=45`）与 PR head（`display_oe=-1`）在同一测试程序下，
  `DRAW1 → sleep → wakeup → DRAW2` 四个标记都出现，末帧 PNG 字节完全相同
  （`b2e0d506…`），面板 QOM 计数也相同（73 帧 / 39959 行）。

## 关键证据

- 数据手册：`evidence/docs-pinmap.txt`（官方 PinMap 全文摘录）、
  `evidence/schematic-nets.txt`（K159-B 第 4 页 pin/net 对照，PDF SHA256 已记录）
- 源码行为：`Bus_EPD::powerControl` / `init` 与 `gpio_hi/lo`、`pinMode` 的负值处理，
  见 `report.md` 的代码位置表
- Host：`evidence/host-checks.txt`、`evidence/npm-test.txt`
- 虚拟设备：`evidence/virtual-device.txt`、`evidence/frames/after-wake-pr-head.png`、
  `evidence/frames/after-wake-base.png`（两文件 SHA256 相同）
- 变更与状态：`evidence/pr-status.json`、`evidence/pr-checks.txt`（40/40 pass）、
  `evidence/pr447.diff`、`evidence/pr447-numstat.txt`
- 可重建工程：`code/`（ESP-IDF 最小工程 + PaperDIY sleep/wakeup 测试程序）

## 文件

- `report.md`：完整报告（事实核验、代码路径、A/B 结果、边界与风险）
- `run.json`：结构化记录
- `evidence/`：原始或派生的可核对证据
- `code/`：可重建的 ESP-IDF 测试工程

## 未覆盖项

- hardware validation：`NOT RUN`。本次没有使用实体 PaperDIY；PR 作者自述做过一次
  sleep/wakeup 实机检查，本次评审未复跑。
- OE 网络的电气行为：虚拟设备不建模 `XOE` / `EPD_PWR` 网络，因此「G45 之前是否真的在
  驱动面板 OE」由原理图与官方 PinMap 判定，不是仿真观测结果。
- 灰度、波形与面板光学：QEMU 只建模 ET047TC1 的数字扫描序列和黑白端点。
- Arduino 目标：本机未装 arduino-cli，未复跑 Arduino 构建；上游 CI 已覆盖。
- 未在真实浏览器打开 board_spec editor 页面；bundle 可逐字节重建已核对。
