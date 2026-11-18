# M5GFX #430：LP I2C 端口在触碰引脚前拒绝驱动不接受的引脚（评审）

- 日期：`2026-11-18`
- 结果：`PARTIAL`（code-level 对照与 host 判定表通过；hardware / virtual-device / build 均为 `NOT RUN`）
- 工作类型：`pr`
- 条目：[m5stack/M5GFX#430](https://github.com/m5stack/M5GFX/pull/430)
  「i2c: refuse pins the LP I2C driver does not accept before touching them」，作者 ainyan03，英文，OPEN，
  处理前评论 0 条、未被 m5agent 回复
- 源码：PR head `5ed5a0df73eaafb4241d9048e517f94d32a27ab0`，base `develop`
  `15d7651faa91c0ef5e0ae53f5ebf0f4db383b51c`（1 file, +19/-4）
- 验证层级：**code-level verification**（与 ESP-IDF 驱动逐条对照）+ **host-level test**
  （把谓词原样抽出，用真实固定对宏与真实 LP IO 引脚集合编译执行）
- 硬件 / 虚拟设备：`NOT RUN`（无 C5 实机与 profile；可用的 C6 / P4 虚拟 profile 不建模 LP 端口的
  焊盘路由）
- GitHub 回复：[issuecomment-6972144303](https://github.com/m5stack/M5GFX/pull/430#issuecomment-6972144303)（英文，单条；PR 保持 OPEN，未 close、未 push）
- 环境：macOS arm64，Apple clang 21.0.0；ESP-IDF 源码按 tag 从公开 GitHub 获取；Device Service
  36 个 profile（无 ESP32-C5）

## 结论

1. 新增的 `lp_pads_accepted()`（`common.inl:1867-1875`）与 ESP-IDF `s_lp_i2c_pins_config()` 的
   引脚接受规则逐条一致：先对 SDA 和 SCL 都做 `rtc_gpio_is_valid_gpio()`，再在
   `!SOC_LP_GPIO_MATRIX_SUPPORTED` 时要求固定对。核对 v5.4.4 / v5.5.4 / v6.0.3 / v6.1.1 四个版本
   均为同一结构。
2. `#if !defined ( LGFX_LP_GPIO_MATRIX )` 的写法在这些目标上与驱动的
   `!SOC_LP_GPIO_MATRIX_SUPPORTED` 等价：M5GFX 只在 SoC 支持 LP GPIO 矩阵且存在
   `<driver/lp_io.h>` 时定义 `LGFX_LP_GPIO_MATRIX`（`:192-196`）；P4 缺该头文件时
   `LGFX_LP_I2C_LEND_PADS` 本身不定义（`:1863-1865`），这段代码不会参与编译。
3. 固定对与 IDF 一致：C6 在四个版本均为 6/7；C5 在 5.4.4 为 6/7，在 5.5.4 / 6.0.3 / 6.1.1 为
   2/3。逐脚 `rtc_io_num_map` 也一致：C5 5.5 的 GPIO7 为 `-1`（LP IO 只剩 0-6），所以 2/3 是
   唯一被驱动接受的组合；C6 为 0-7；P4 为 0-15。
4. 放置位置正确：检查是 LP 分支的第一条语句（`:2336-2342`），在 `release_lp_pad()` /
   `pinMode()` / `i2c_stop()`（`:2343-2351`）之前。`init(port, sda, scl)` 先经 `setPins()`
   （`:2454-2462`）配置引脚，因此 `init()` 执行到此处时上下文尚未初始化，检查不会碰任何焊盘。
5. 无阻塞项。两条非阻塞观察：`LGFX_LP_I2C_LEND_PADS` 生效时，`:2363` 的
   `const bool lp_pads = ...` 已恒真；在没有 `LP_I2C_*_IOMUX_PAD` 的旧 SDK 上固定对检查会编译掉，
   有效但非法的引脚仍会走到驱动并落入旧失败路径（5.4.3+ 均定义，影响面仅限更旧的 SDK）。
6. 仍未闭环的是运行时证据：作者明确未在 C5 / C6 实机运行。P4 实测走的是矩阵路径（任意有效 LP
   对都接受），因此「有效但非固定对被拒绝且其 IO MUX 路由保持不变」这一点只在代码层成立，已在
   回复中请作者补一次 C5 或 C6 的对照。

## 关键证据

- `evidence/pr-430.diff`：PR 全量差分（1 file, +19/-4）。
- `evidence/source-lines.txt`：PR head 的宏定义、新谓词、`init()` 调用点、`setPins()` 入口。
- `evidence/idf-pin-checks.txt`：ESP-IDF 四个版本的 `s_lp_i2c_pins_config()` 原文、逐脚
  `rtc_io_num_map`、C5/C6 固定对宏、SoC caps。
- `evidence/host-predicate/`：原样抽出的谓词、host 工程与五个配置的判定表输出（全部 PASS）。
- `evidence/ci-checks.txt`：PR 的 26 项 CI（全部 pass，仅构建）。
- `evidence/device-profiles.txt`、`evidence/emulator-lp-i2c-search.txt`：可用虚拟 profile 与
  LP I2C / LP IO 模型的检索结果（无模型）。
- `evidence/reply-430.md` / `evidence/reply-posted.txt`：投稿英文回复与投稿结果。

## 未覆盖项

- hardware validation：`NOT RUN`。本机没有 ESP32-C5 / C6 实机；作者 P4 的 GPIO11/9 与
  GPIO18/19 结果是引用，未复现。
- virtual-device validation：`NOT RUN`。没有 C5 profile；C6 / P4 profile 存在，但本变更的可观测
  差异是 LP IO 焊盘路由是否被改动，本地 esp-emulator 检出中没有 LP I2C 控制器 / LP IO 路由模型，
  跑固件只能得到与改动前相同的 `invalid_arg` 返回值，无法区分新旧实现。
- build：`NOT RUN`。本机未安装 Arduino / PlatformIO，也没有本地 ESP-IDF 工具链；PR 的 26 项 CI
  构建全部 pass 作为引用。
- C5 / C6 上「有效但非固定对被拒绝后路由保持不变」：`NOT RUN`（作者亦未运行）。

## 文件

- `report.md`：背景、代码事实、IDF 对照、判定表、影响面与未覆盖项
- `run.json`：结构化状态
- `evidence/`：差分、源码摘录、IDF 摘录、host 判定表、CI、profile 与模型检索、回复
