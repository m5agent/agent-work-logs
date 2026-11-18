# M5GFX #433 评审报告：LP I2C FIFO 深度未知时中止构建

## 1. 背景与目标

`m5stack/M5GFX#432`（作者 GOB52）把 FIFO 深度的取值源从 `soc_caps.h` 的 `SOC_*`
切到 `hal/i2c_ll.h` 的 `I2C_LL_*`，修好了 ESP-IDF 6.x 下 LP 端口按 32 字节分块写入
16 字节 FIFO 的问题。#432 的评审中我提了两条非阻塞建议，其中一条是：LP 端口存在但两个
深度宏都不存在时，`#else` 会静默返回 HP 深度，应改成 `#error`。作者表示交给维护者决定。

本 PR #433（作者 ainyan03）就是那条建议的实现，+3 行，只改 `getFifoLen()`。

评审要回答三件事：

1. 这个守卫会不会在现网受支持的配置上误触发（把能编的配置编坏）；
2. 守卫的位置和写法是否正确；
3. 该触发时是否真的能停下构建，并给出可诊断的信息。

## 2. 改动范围

`src/lgfx/v1/platforms/esp32/common.inl`，+3/-0：

```cpp
#elif LGFX_LP_I2C_NUM > 0
      // Falling back to the HP depth would overrun the shallower LP FIFO without any error.
 #error "LP I2C FIFO depth is unknown: neither SOC_LP_I2C_FIFO_LEN nor I2C_LL_LP_FIFO_LEN is defined"
```

- base 是 `develop` 的 `e88846e`，即 #432 的 merge commit，所以 #432 的 `I2C_LL_*`
  分支已在 base 里，PR 只叠了这三行。
- `LGFX_LP_I2C_NUM` 在 `common.inl:121-130` 推导：SDK 定义 `SOC_LP_I2C_NUM > 0`、
  有 `<driver/i2c_master.h>`、`ESP_IDF_VERSION >= 5.4` 三者同时成立才为 1，否则为 0。
  因此该守卫只在「SDK 认可 LP 端口」的前提下生效，不会波及 HP-only 芯片。
- `getFifoLen()` 的两个调用点是 `common.inl:2760`（`txfifo_limit`）与 `:2802`
  （`rxfifo_limit`），没有第三处直接引用 LP 深度宏。
- 同一文件 `common.inl:744-746` 已有 `#error "LGFX_LP_I2C_NUM must be defined before
  release_lp_pad"`，写法与风格一致。

## 3. 方法

### 3.1 头文件普查（真实 tag，不依赖 release notes）

`code/probe-lp-macros.sh` 对 14 个 ref（`v5.4.1 v5.4.2 v5.4.3 v5.5.1 v5.5.2 v5.5.3
v5.5.4 v6.0 v6.0.1 v6.0.2 v6.0.3 v6.1.1 master v6.3-dev`）× 8 个芯片（`esp32
esp32c2 esp32c5 esp32c6 esp32c61 esp32h4 esp32p4 esp32s31`）下载 `soc_caps.h` 与
`hal/i2c_ll.h`，记录 `SOC_LP_I2C_NUM`、`SOC_LP_I2C_FIFO_LEN`、`I2C_LL_LP_FIFO_LEN`
的存在性与取值，以及 `i2c_ll.h` 的位置。共 112 行，见
`evidence/lp-fifo-macro-survey.tsv`。

说明：`v5.4.0` / `v5.5.0` 不是存在的 tag（API 返回 404），所以 5.4 系的下界取 5.4.1。

### 3.2 抽取函数编译（base 对 head）

`code/extract_fifo_fn.py` 从 base/head 的 `common.inl` 原文抽出 `isLpPort()` +
`getFifoLen()`（不改一个字），用普查得到的真实宏组合逐个编译运行
（`-std=c++17 -Wall -Wextra -Werror`）：

| 配置 | 宏 | 期望 |
| --- | --- | --- |
| 6.x C5/C6 | `LGFX_LP_I2C_NUM=1`, `LGFX_LP_I2C_PORT=1`, `I2C_LL_FIFO_LEN=32`, `I2C_LL_LP_FIFO_LEN=16` | HP 32 / LP 16 |
| 6.x P4 | 同上，`LGFX_LP_I2C_PORT=2` | HP 32 ×2 / LP 16 |
| 6.x C2 / ESP32 | `LGFX_LP_I2C_NUM=0` + `I2C_LL_FIFO_LEN` 16 / 32 | 16 / 32 |
| 5.x C5/C6/P4 | `SOC_I2C_FIFO_LEN=32`, `SOC_LP_I2C_FIFO_LEN=16` | HP 32 / LP 16 |
| 5.x ESP32 | `SOC_I2C_FIFO_LEN=32`, 无 LP | 32 |
| 合成：LP 端口 + 只有 HP 深度宏 | `LGFX_LP_I2C_NUM=1` + 仅 `SOC_I2C_FIFO_LEN` 或仅 `I2C_LL_FIFO_LEN` | base 返回 32；head 必须编译失败 |

## 4. 观察

### 4.1 现网配置不会落到新分支（普查结果）

| tag 区间 | LP 芯片 | `SOC_LP_I2C_NUM` | `SOC_LP_I2C_FIFO_LEN` | `I2C_LL_LP_FIFO_LEN` |
| --- | --- | --- | --- | --- |
| 5.4.1〜5.5.4 | C5 / C6 / P4 | `(1U)` | `(16)` | 不存在 |
| 5.5.1〜5.5.4 | H4 | `(1U)` | `(16)` | 不存在 |
| 6.0〜6.1.1 / master / 6.3-dev | C5 / C6 / P4 | `(1U)` | 不存在 | `16` |
| 6.1.1 / master / 6.3-dev | S31 | `(1U)` | 不存在 | `16` |
| 全部 tag | C61 | 不存在 | 不存在 | 不存在 |
| 6.0 起 | H4 | 不存在 | 不存在 | 不存在 |

- 没有任何 tag 出现「`SOC_LP_I2C_NUM` 存在但两个深度宏都缺失」，所以
  `LGFX_LP_I2C_NUM == 1` 时必有一个深度宏可用，新分支在 5.4.1〜6.1.1 与当前 master 上
  都不可达。作者的陈述成立，且「6.1.1 的 S31 preview target」也确实如此。
- C61 在所有 tag 里都没有 LP I2C caps，H4 在 6.0 起 LP caps 消失——两者的
  `LGFX_LP_I2C_NUM` 都会是 0，不会触发该守卫。
- 6.x 的 `hal/i2c_ll.h` 移到 `components/esp_hal_i2c/<chip>/include/hal/`，include 名
  不变，`common.inl:72-74` 的 `#include <hal/i2c_ll.h>` 依旧解析得到。

### 4.2 能编过的配置生成代码不变，该停的配置确实停

`evidence/host-harness-output.txt`：

- head 与 base 在 7 个真实配置上返回值完全一致（32/16、P4 的 32/32/16 等），本 PR 不改
  任何已编译代码。
- 合成「LP 端口 + 只有 HP 深度宏」：base 编译通过并把 LP 端口报成 32（正是 #432 修的
  那类静默错误）；head 在两种变体（只有 `SOC_I2C_FIFO_LEN`、只有 `I2C_LL_FIFO_LEN`）
  都中止，报错原文为
  `error: "LP I2C FIFO depth is unknown: neither SOC_LP_I2C_FIFO_LEN nor I2C_LL_LP_FIFO_LEN is defined"`。
- 无 LP 端口的配置（C2 / ESP32）在 head 下照常编过，没有因为新增分支产生未使用变量或
  参数警告。

### 4.3 CI 仍未编译这一行

- `IDFBuild.yml` 的 6.x 作业只有 `esp32` / `esp32s3`（6.0.2），这两个芯片没有 LP 端口；
  C5（5.5.2）、C6（5.4.3）、P4（5.4.3）、C61（5.5.2）全在 5.x。
- `ArduinoBuild.yml` 最高到 core 3.3.0（ESP-IDF 5.5.0），仍是 `SOC_*` 时代。
- 因此新增的 `#elif ... I2C_LL_LP_FIFO_LEN` 在 CI 中永远不会被选中；PR 的 20 个检查全绿，
  但对这三行没有覆盖力。「Fork CI passed」不构成这一行的证据。

## 5. 结论与建议

无阻塞问题，方向正确：把一个静默的错误变成构建期错误，且当前不会误伤任何已发布 SDK。

非阻塞建议：

1. **CI**：给 6.x 加一个 LP 机型（`esp32c6` + `6.0.2` 即可），让新的 `#elif` 至少被编译
   一次；`#error` 分支只能靠人为缺失宏的构建覆盖，可以接受长期不覆盖。
2. **报错信息**：可以带上目标与 IDF 版本（例如把 `__FILE__` 换成
   `CONFIG_IDF_TARGET`/`ESP_IDF_VERSION` 的字符串化宏），现场排查更快。`LGFX_LP_I2C_NUM`
   在库里是硬定义、用户不能覆盖，所以目前没有「关掉 LP 端口继续编」的逃生口，报错里也
   不必提。
3. **守卫边界**：本 PR 只覆盖「深度宏改名」。若未来 SDK 让 `SOC_LP_I2C_NUM` 本身消失
   （H4 在 5.5.x→6.0 就是这样），`LGFX_LP_I2C_NUM` 会静默变 0、LP 端口整个不参与编译，
   这个 `#error` 看不到。属于本 PR 之外的范围，记录在此以免被当成「已完全防住」。

## 6. 影响面与回滚

- 影响面：仅 ESP-IDF ≥ 5.4 且 SDK 认可 LP 端口的构建；所有已发布 tag 的行为不变。
- 回滚：删除这三行即可恢复「静默返回 HP 深度」的旧行为，无 ABI / 数据布局变化。

## 7. 未覆盖

- hardware validation：`NOT RUN`。无 C5/C6/P4 实机；#432 的实机数据与作者报告的
  IDF 6.1 / P4 构建未复现。
- virtual-device validation：`NOT RUN`，结构性不可得（见 README 说明）。
- 本机未跑 ESP-IDF 6.x 原生构建：Docker 无法创建容器（
  `write /var/lib/desktop-containerd/.../meta.db: read-only file system`）。
- `#error` 分支本身：只有合成构建，没有真实 SDK 能触发。
