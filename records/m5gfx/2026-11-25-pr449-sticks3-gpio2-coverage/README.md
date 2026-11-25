# M5GFX #449：StickS3 清 M5PM1 gpio2 功能位；board_t 覆盖测试

- 日期：`2026-11-25`
- 结果：`PARTIAL`（virtual-device validation + host-level test + code-level verification；
  真机与“复位前遗留功能位”场景 `NOT RUN`）
- 工作类型：`pr-review`
- 问题来源：[m5stack/M5GFX#449](https://github.com/m5stack/M5GFX/pull/449)，作者 `ainyan03`，
  英文，OPEN；评审前 comments / reviews 均为 0
- 源码版本：head `5b65db1f8a7a66cbe6051c596bd1e78bcf62a4fb`，
  base `34a5756d004a4475c48ba55dcf7725bb1fc367cd`（= `develop` tip，`git ls-remote` 核对）
- 环境：macOS arm64；ESP-IDF v6.1 构建 ESP32-S3 探针固件；本机 Device Service 的 `sticks3`
  profile（QEMU `m5sticks3`，ST7789P3 135×240，`simulated`）

## 结论

两条改动都成立，未发现阻塞合并的问题。

1. `sticks3_power_on` 把 `0x16` 的清除掩码从 `0x04` 改为 `0x30` 是正确的：M5PM1 的
   `GPIO_FUNC0`（`0x16`）每个引脚占 2 bit，gpio2 在 bit5:4；`0x04` 落在 gpio1 的 bit2 上。
   M5Unified 的 `setGPIOFunction()` 与 M5GFX 自己给 P4 Hub GPIO3 写的 `0x16 = 0xC0`
   （bit7:6）都印证同一布局，ToughC5 / PaperDIY 也早已用 `0x30`。
2. 新增的 `board_id_coverage.test.js` 在 `npm test` 与上游 `Catalog and generated sources`
   CI 中通过；对“目录缺 `legacy_board_id`”“`board_t` 重复数值”“从 `<chip>_boards[]` 删掉
   definition”三类改坏都能报错，快照可用 `M5GFX_UPDATE_SNAPSHOTS=1` 原样重生成（无残留 diff）。

唯一建议（非阻塞）：测试只要求“某个” `<chip>_boards[]` 里有该 definition，没有把表所属
芯片与 catalog 的 `chip` 绑定；把 StickS3 的 `board_entry` 从 `esp32s3_boards[]` 挪到
`esp32p4_boards[]` 仍然 PASS（实测），而 `select_fixed_board()` 只查当前 target 的表，
这种错放会让本机不可选、错机可选。当前 64 块板 catalog `chip` 与所在表 0 处不一致，
补这条断言不需要白名单。

## 关键证据

- 虚拟设备（`sticks3` profile）：同一探针固件，head 与 base 都 `fixed_init=1 board=26
  display=135x240`，`func0_after_init=0x00 gpio2_func=0 gpio1_func=0`，135×240 画面
  sha256 均为 `fa740237…8357`；即打补丁后设备路径正常、`0x16` 在 `begin` 后读到 `00`，
  与作者真机读数一致。base 在复位态也是 `00`，所以这一轮**不能区分**两版掩码，
  区分力来自 host 快照与代码事实。
- host：`npm test` 217 pass / 0 fail / 5 skipped（缺 M5Unified checkout），
  `npm run check` 通过（64 boards / 91 combinations），`test/board_detect/run.sh` 34/34，
  快照重生成无 diff。
- 上游 CI：40/40 全部 pass。
- 代码事实：`src/board_detect/m5/pmic_ops.hpp:89`、`src/M5GFX.cpp:156,644`、
  `extras/board_spec/boards/m5sticks3.json`（gpio2 → `dev:lcd.power`）。

## 文件

- `report.md`：完整报告（根因、影响面、验证过程、边界）
- `run.json`：结构化记录
- `evidence/pr449.diff`：PR 完整差异（base `34a5756` → head `5b65db1`）
- `evidence/code-facts.txt`、`evidence/m5unified-facts.txt`：行号级代码事实
- `evidence/build-info.txt`：构建、产物、会话、串口与画面关键值
- `evidence/serial-head.txt`、`evidence/serial-base.txt`：两版完整串口
- `evidence/frame-head.png`、`evidence/frame-base.png`：135×240 截图（同 SHA256）
- `evidence/npm-test-head.txt`、`evidence/npm-check-head.txt`、`evidence/board-detect-head.txt`
- `evidence/snapshot-regen.txt`、`evidence/snapshot-regen-diff.txt`：快照重生成与空 diff
- `evidence/mutation-*.txt`：覆盖测试的四组变异验证
- `evidence/harness-main.cpp`：探针固件 `main.cpp`
- `evidence/device-profile.json`、`evidence/pr-metadata.json`

## 未覆盖项

- hardware validation：`NOT RUN`。本机无 StickS3 实物；作者正文的真机读数只作为引用。
- “复位前遗留 `0x16` ≠ 0”的场景 `NOT RUN`：本 profile 的 guest 软复位不进入第二次启动，
  Device Service `POST /reset` 在 boot 阶段 panic；且在 `M5GFX::init()` 之前建过 I2C master
  总线（IDF 驱动建后删除，或 lgfx 直接读写）会让 fixed 启动失败（`fixed=26, init=0`，
  连写回 `0x00` 也一样），所以无法在同一 boot 内预置该寄存器。
- 自动识别路径 `NOT RUN`：M5GFX 的检测器在该 profile 上不确认（`candidate=0`），
  探针改用 `fixed_board`；两条路走同一 descriptor 与同一段 power ops，但运行时自动识别未跑。
- 旧代码“gpio1 功能被改坏”的实际后果（是否影响按键/中断）未在真机观察。
