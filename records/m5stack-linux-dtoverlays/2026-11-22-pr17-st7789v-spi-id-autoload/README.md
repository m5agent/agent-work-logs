# m5stack/m5stack-linux-dtoverlays #17：Cardputer Zero 的 st7789v LCD 驱动自动加载

- 日期：`2026-11-22`
- 结果：`REVIEW`（代码级验证通过；运行时行为未在本机复现）
- 工作类型：`pr_review`
- 条目：[m5stack/m5stack-linux-dtoverlays#17](https://github.com/m5stack/m5stack-linux-dtoverlays/pull/17)
  「st7789v: autoload the LCD driver on the Cardputer Zero」，作者 khalifa-mnt，英文，
  OPEN，无历史评论，无 review
- 源码：PR head `40022b4a0f0c2d27347c9b520895475dd46b2c21`，base `main`
  `a3fd3e83c0247e16e194e7e40f7fc1f5be933dd4`；1 文件，`+5/-0`
- 环境：macOS arm64；本机无 Cardputer Zero 硬件；本地 Device Service 的
  `cardputer-zero` profile 为 Linux ARM64 后端且不可创建；无 Linux 内核头文件或
  交叉工具链可重建模块
- 已发布回复：<https://github.com/m5stack/m5stack-linux-dtoverlays/pull/17#issuecomment-7087026741>
  （1 条，英文；PR 仍 OPEN，未 close、未 push 上游、未改他人代码）
- 证据等级：**code-level verification**（Raspberry Pi 6.1.y / 6.6.y 内核源码 +
  PR 源码 + 提交者自述的硬件结果）

## 结论

补丁正确且最小，无阻塞问题。

1. 两个 overlay 的 LCD 节点首个 compatible 都是
   `cardputerzero,st7789v_lcd`。Raspberry Pi 6.1.y 的 `of_modalias_node()` 与 6.6.y 的
   `of_alias_from_compatible()` 都只取 compatible 列表第一项、去掉第一个逗号之前的
   vendor 前缀，得到 `st7789v_lcd`；SPI 设备的 sysfs `modalias` 与 uevent 都是
   `spi:` + 该值，因此设备侧是 `spi:st7789v_lcd`，且没有 `of:` modalias。
2. 驱动原来的 SPI id 表只有 `panel-mipi-dbi-spi` / `panel-mipi-dbi-m5stack`，没有
   `st7789v_lcd`，所以 udev 按 modalias 找不到模块。新增 `{ "st7789v_lcd", 0 }` 后，
   `MODULE_DEVICE_TABLE(spi, ...)` 经 `scripts/mod/file2alias.c::do_spi_entry()`
   生成 `spi:st7789v_lcd` 别名，正好匹配设备 modalias。
3. 首个 compatible 必须保留：`panel_mipi_dbi_commands_from_fw()` 用
   `of_property_read_string_index(..., "compatible", 0, ...)` 拼出
   `cardputerzero,st7789v_lcd.bin`。补丁没有改它，固件加载路径不变；驱动仍可通过
   `of_match_table` 里的第二个 compatible `panel-mipi-dbi-m5stack` 绑定。
4. 覆盖面完整：仓库内只有 Cardputer Zero v3 / v5 两个 overlay 使用
   `panel-mipi-dbi-m5stack`，两者的首个 compatible 相同，一个 id 表条目同时覆盖两块板。
   `99-cardputer-zero-lcd.rules` 只创建 DRM / fb 符号链接，不做 modprobe，说明
   autoload 缺口确实只能由驱动别名补。
5. 提交者在真实 Cardputer Zero 上自测：不加 modprobe alias、不用 `i2cprobe` 时，
   开机自动加载 `panel_mipi_dbi_m` 并出 console。该运行时结果未在本记录中独立重跑。

## 关键证据

- `evidence/kernel-modalias.txt`：6.1.y `of_modalias_node()`、6.6.y
  `of_alias_from_compatible()`、`spi_uevent()`、`spi_match_id()` 与
  `do_spi_entry()` 的原文和行号；证明设备 modalias 是首个 compatible 去 vendor
  前缀，模块别名是 `spi:<id name>`。
- `evidence/module-and-overlays.txt`：PR head 的 SPI id 表与固件加载代码、v3 / v5
  overlay 行号、`panel-mipi-dbi-m5stack` 的全部使用者、udev 规则、`.bin` SHA256。
- `evidence/pr-diff.txt`：PR 差分、base/head、`git apply --check` 通过。
- `evidence/pr-metadata.txt`：PR 状态、作者、`+5/-0`、无评论/无 review、唯一检查是
  WeCom 摘要转发（没有内核模块构建作业）。
- `evidence/local-profile-summary.txt`：`cardputer-zero` profile 为
  `supported=false`、`creatable=false`、`backend_ready=false`，缺少 QEMU / ROM。
- `evidence/hardware-bench-summary.txt`：硬件台 5 个节点均为 ESP32 / ESP32-P4 类，
  没有 Cardputer Zero 或 Linux ARM64 / Broadcom 目标。

## 未覆盖项

- hardware validation：`NOT RUN`。本机没有 Cardputer Zero，硬件台也没有该机型；
  提交者的自测是该项的唯一运行时证据。
- virtual-device validation：`NOT RUN`。`cardputer-zero` profile 明确不可创建，
  `missing_runtime_files` 为 `__missing_qemu__` / `__missing_rom__`，且其后端是
  Linux ARM64，不是 ESP32 固件目标。
- 开机 autoload 与 `/dev/fb_lcd` / console：`NOT RUN`，原因同上；本记录只验证到
  「代码与内核规则会产生正确的 `spi:st7789v_lcd` 别名」。
- 模块重建：`NOT RUN`。本机无 Linux 内核头文件 / 交叉工具链，未独立编译；
  改动只是 id 表追加，且已确认 patch 能干净应用到 base。
- CI 构建：`NOT RUN`。仓库只有 WeCom 摘要转发工作流，没有构建该模块的 CI。

## 文件

- `report.md`：完整评审、机制、验证矩阵与边界
- `run.json`：机器可读记录
- `evidence/`：内核源码、PR、模块与平台状态证据
- `patches/0001-st7789v-lcd-spi-id.patch`：PR 差分（base `a3fd3e8`）
