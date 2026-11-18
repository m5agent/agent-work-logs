# M5GFX #433: LP I2C FIFO 深度未知时中止构建（代码级验证）

- 日期：`2026-11-18`
- 结果：`PARTIAL`（代码与头文件层面验证通过；实机、虚拟设备 `NOT RUN`）
- 工作类型：`pr`
- 条目：[m5stack/M5GFX#433](https://github.com/m5stack/M5GFX/pull/433)
  「i2c: stop the build when the LP I2C FIFO depth is unknown」，作者 ainyan03，英文，OPEN
- 源码：PR head `99eb30e815438bc01bd2a114992db5c0e076acd4`，base `develop`
  `e88846e781091ff489de3afb5770f7333af1d864`（即 #432 的 merge commit）
- 环境：macOS arm64；Apple clang 21.0.0；ESP-IDF 各 tag 头文件取自 upstream
  raw；本机 Docker 无法创建容器（containerd 元数据只读），没有跑成 6.x 原生构建

## 结论

1. 改动正确、位置正确。`getFifoLen()` 里 `LGFX_LP_I2C_NUM > 0` 且两个深度宏都不存在时，
   现在用 `#error` 停构建；同一文件 `common.inl:745` 已有同样风格的 `#error`，写法一致。
2. 「现网没有配置会落到这个分支」成立，而且范围比作者描述的更完整：5.4.1〜5.5.4 的
   C5/C6/P4（H4 自 5.5.1）都是 `SOC_LP_I2C_NUM=(1U)` + `SOC_LP_I2C_FIFO_LEN=(16)`
   成对出现；6.0〜6.1.1、master、v6.3-dev 都是 `SOC_LP_I2C_NUM=(1U)` +
   `I2C_LL_LP_FIFO_LEN 16` 成对出现。没有任何 tag 出现「有 LP 端口数、没有深度宏」。
3. 抽出 base/head 的 `isLpPort()`+`getFifoLen()` 用真实宏组合编译：能编过的配置里，
   base 与 head 的返回值完全相同，说明本 PR 不改动任何已编译代码；人为造出「只有 HP
   深度宏」的配置时，base 静默返回 32（本 PR 要消除的那类错误），head 按预期中止并给出
   消息。
4. 无阻塞问题。两条非阻塞建议见 `report.md`：CI 仍没有 6.x 的 LP 机型作业，这一行从未
   被编译；以及该守卫只覆盖「深度宏改名」，不覆盖「LP 端口数宏消失」。

## 关键证据

- `evidence/lp-fifo-macro-survey.tsv`：14 个 tag（5.4.1〜6.1.1、master、v6.3-dev）×
  8 个芯片共 112 行，逐个记录三个宏是否存在与取值、`hal/i2c_ll.h` 在 5.x/6.x 的路径。
- `evidence/host-harness-output.txt`：base/head 各 7 个真实配置 + 2 个合成配置的编译与
  返回值，含 `#error` 的原始报错行。
- `evidence/ci-matrix.txt`：`IDFBuild.yml` / `ArduinoBuild.yml` 矩阵与本 PR 的 20 个检查。
- `evidence/diff-scope.txt`：base/head、+3 行差分、`git apply --check` 结果、
  `getFifoLen()` 的两个调用点（`common.inl:2760` / `2802`）。
- `code/`：`probe-lp-macros.sh`、`extract_fifo_fn.py`、`fifo_harness.cpp`、`run.sh`；
  `bash code/run.sh <M5GFX clone>` 可重建全部输出。
- `patches/0001-i2c-lp-fifo-error.patch`：PR head 的差分，已在 base `e88846e` 上
  `git apply --check` 通过。
- 已发布回复：<https://github.com/m5stack/M5GFX/pull/433#issuecomment-6981823847>（1 条，
  英文；PR 仍 OPEN，未 close、未 push 上游）

## 未覆盖项

- hardware validation：`NOT RUN`。本机没有 C5 / C6 / P4 实机；作者报告的各版本构建与
  #432 的实机数据未复现。
- virtual-device validation：`NOT RUN`，且是结构性的：改动只决定翻译单元能否编过，
  任何能编过的配置生成的代码与 base 完全相同，模拟设备上不可能出现差异；唯一的可观测量
  是「构建停不停」。
- ESP-IDF 6.x 原生构建：本机未跑（Docker 无法创建容器：containerd 元数据只读）。
  依赖作者报告的 P4 / IDF 6.1 构建 + 上面的头文件普查 + CI 矩阵结论。
- `#error` 分支本身不可能被 CI 覆盖（需要「人为缺失宏」的构建），这一条无法以现有 CI
  形式验证。
