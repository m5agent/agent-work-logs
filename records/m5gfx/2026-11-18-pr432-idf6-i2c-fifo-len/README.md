# M5GFX #432: I2C FIFO 深度改从 `hal/i2c_ll.h` 读取（代码级验证）

- 日期：`2026-11-18`
- 结果：`PARTIAL`（代码与头文件层面验证通过；实机、虚拟设备 `NOT RUN`）
- 工作类型：`pr`
- 条目：[m5stack/M5GFX#432](https://github.com/m5stack/M5GFX/pull/432)
  「i2c: ESP-IDF 6.0 以降で FIFO の深さを hal/i2c_ll.h から取る」，作者 GOB52，日文，OPEN
- 源码：PR head `c90dda61ae3718ea90f48c249055d38698e1f1f6`，base `develop`
  `452c15bc982af0b54acf567a79e7eb6066ace9e5`
- 环境：macOS arm64；Apple clang 21.0.0；ESP-IDF 各 tag 的头文件直接取自 upstream
  （本机没有 6.x 工具链）

## 结论

1. 改动正确，且恰好命中问题。6.0 起 `soc_caps.h` 里已没有 `SOC_I2C_FIFO_LEN` /
   `SOC_LP_I2C_FIFO_LEN`，深度改由 `hal/i2c_ll.h` 的 `I2C_LL_FIFO_LEN` /
   `I2C_LL_LP_FIFO_LEN` 提供，数值与 5.x 相同（C5/C6/P4 的 LP 16、HP 32；C2 的 HP 16；
   ESP32/S3 的 HP 32）。
2. 5.3 / 5.4.3 / 5.5.4 仍有 `SOC_*`，且完全没有 `I2C_LL_*`，所以新增的 `#elif` 在 5.x 是
   死代码，行为不变——与作者描述一致。
3. 把 `isLpPort` / `getFifoLen` 从 head 原文抽出，按真实头文件的宏组合编译
   （`-Wall -Wextra -Werror`）：C5/C6 为 HP 32 / LP 16；P4 为 HP 32 ×2 / LP(port 2) 16；
   C2 为 16。base 下 LP 与 C2 都是 32，复现了报告中的现象。
4. `writeBytes` 的首块算式在 `txfifo_limit` 为 32 时，17 字节起首块就超过 16——与
   「C5/C6 从 18 字节、P4 从 17 字节开始失败」的边界吻合；改成 16 后 9~97 字节全部按 ≤16
   分块，且各块之和等于原长度。
5. 无阻塞问题。两条非阻塞建议：CI 的 6.x 矩阵里没有 LP 机型，新分支从未被编译；以及
   「有 LP 端口但两个宏都不存在」时会静默返回 HP 深度，建议改成 `#error`。

## 关键证据

- `evidence/idf-fifo-macro-probe.tsv`：`v5.3`〜`v6.3-dev` × C5/C6/P4/C2/ESP32 共 30 行，
  记录宏是否存在、取值，以及 `hal/i2c_ll.h` 的位置（5.x 在 `components/hal/<chip>/`，
  6.x 在 `components/esp_hal_i2c/<chip>/`）。
- `evidence/code-level-run.txt`：抽取函数的编译与运行（head 对 base），以及写入分块模拟。
- `evidence/write-chunk-sim.txt`：分块模拟摘录。
- `evidence/getfifolen-diff.txt`：base→head 的 5 行改动（`common.inl:1461` 附近）。
- `evidence/ci-matrix.txt`：`IDFBuild.yml` / `ArduinoBuild.yml` 矩阵。6.x 作业只有
  `esp32` / `esp32s3`（6.0.2），C5/C6/P4 全在 5.x；Arduino 最高 3.3.0（ESP-IDF 5.5.0）。
- `code/`：`probe-macros.sh`、`extract_fifo_fn.py`、`fifo_harness.cpp`、
  `write_chunk_sim.cpp`、`run.sh`；`bash code/run.sh <M5GFX clone>` 可重建全部输出。
- `patches/0001-i2c-idf6-fifo-len.patch`：PR head 的差分，已在 base `452c15b` 上
  `git apply --check` 通过。
- 已发布回复：<https://github.com/m5stack/M5GFX/pull/432#issuecomment-6977090203>（1 条，日文；PR 仍 OPEN，未 close、未 push 上游）

## 未覆盖项

- hardware validation：`NOT RUN`。本机没有 ToughC5 / Nesso N1 / Tab5 实机；作者的 NFC
  检测次数与 `test_UnitNFC_ToughC5` 181/181 未复现。
- virtual-device validation：`NOT RUN`。原因是：(1) 改动只在用 ESP-IDF 6.x 编译时才生效，
  本机编译链只有 5.4 / 5.5，没有 6.x 工具链与镜像（也未拉取 Docker 镜像）；(2) 5.x 下新增
  分支会被预处理器排除，base 与 head 的二进制完全相同，模拟设备上无法产生差异；
  (3) Device Service 虽有 `nesso-n1`（C6）与 `tab5`（P4）profile，但没有确认存在能观测
  LP I2C FIFO 深度溢出的模型。
- ESP32-C2：无实机、无 6.x 构建，仅有头文件取值与分支评估。
- 作者执行的 5.4.4 / 5.5.4 / 6.0.3 / 6.1 原生构建未重跑。
