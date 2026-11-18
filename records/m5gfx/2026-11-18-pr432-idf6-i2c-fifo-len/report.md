# M5GFX #432 评审报告（ESP-IDF 6.0 的 I2C FIFO 深度宏迁移）

## 1. 背景

M5GFX 的 ESP32 系列 I2C 实现在 `src/lgfx/v1/platforms/esp32/common.inl`，按端口返回
硬件 FIFO 深度（`getFifoLen()`），`writeBytes()` / `readBytes()` 用它切分传输。低功耗
（LP）I2C 的 FIFO 比 HP 浅，因此该函数先看 `SOC_LP_I2C_FIFO_LEN`，只对 LP 端口返回浅值。

ESP-IDF 6.0 把这两个宏从 `soc_caps.h` 移走，改到 `hal/i2c_ll.h`，名字变成
`I2C_LL_FIFO_LEN` / `I2C_LL_LP_FIFO_LEN`。代码仍只看 `SOC_*`，预处理于是落到最后的
`return 32;`，LP 端口也拿到 32。

PR #432 加 5 行：`SOC_*` 不存在时，用 `I2C_LL_*` 的两个 `#elif`。

## 2. 代码事实

- 改动只有 `getFifoLen()`（head `c90dda6`，base `452c15b`）。
  见 `patches/0001-i2c-idf6-fifo-len.patch` 与 `evidence/getfifolen-diff.txt`。
- `<hal/i2c_ll.h>` 在 `common.inl:72-74`，条件为
  `#if (ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 3, 0))` 加 `__has_include`，本来就已经
  include。6.x 里该文件的实体搬到 `components/esp_hal_i2c/<chip>/include/hal/`，但
  `hal/i2c_ll.h` 这个 include 名仍然可解析。
- 调用点只有两个：`writeBytes()` 的 `txfifo_limit`（`common.inl:2757`）与 `readBytes()` 的
  `rxfifo_limit`（`:2799`）。写入首块为 `((length - 1) % txfifo_limit) + 1`，之后固定
  `txfifo_limit`。
- `LGFX_LP_I2C_NUM` 仅在 `SOC_LP_I2C_NUM > 0`、存在 `<driver/i2c_master.h>` 且
  `ESP_IDF_VERSION >= 5.4.0` 时非 0（`common.inl:125-130`）。6.x 仍保留
  `SOC_LP_I2C_NUM`，所以新增的 `#elif` 可达——只有 C5/C6/P4。
- LP 端口号排在 HP 端口之后（`LGFX_LP_I2C_PORT = LGFX_HP_I2C_NUM`）。

## 3. 方法

1. **头文件实物**：`code/probe-macros.sh` 从 upstream 抓 `soc_caps.h` 与 `hal/i2c_ll.h`，
   覆盖 `v5.3` / `v5.4.3` / `v5.5.4` / `v6.0` / `v6.0.3` / `v6.1.1` / `v6.3-dev` ×
   `esp32` / `esp32c2` / `esp32c5` / `esp32c6` / `esp32p4`，输出宏的有无与取值
   （`evidence/idf-fifo-macro-probe.tsv`）。
2. **分支评估**：`code/extract_fifo_fn.py` 从 base 与 head 原文抽出
   `isLpPort()` / `getFifoLen()`；`code/fifo_harness.cpp` 按真实头文件的宏组合用
   `-Wall -Wextra -Werror` 编译并运行（`code/run.sh`）。
3. **分块算术**：`code/write_chunk_sim.cpp` 复用 `writeBytes()` 的同一式子，对每组
   `limit` × 硬件深度求最大单块。
4. **CI 覆盖**：读 head 的 `IDFBuild.yml` / `ArduinoBuild.yml` 矩阵。

## 4. 结果

### 4.1 宏的位置（节选，全部 30 行见 TSV）

| ref | SOC_I2C_FIFO_LEN | SOC_LP_I2C_FIFO_LEN | I2C_LL_FIFO_LEN | I2C_LL_LP_FIFO_LEN |
| --- | --- | --- | --- | --- |
| 5.3 / 5.4.3 / 5.5.4（C5/C6/P4/C2/ESP32） | 有（C2 为 16，其余 32） | 有（C5/C6/P4 为 16） | 无 | 无 |
| 6.0 / 6.0.3 / 6.1.1（C5/C6/P4） | 无 | 无 | 32 | 16 |
| 6.0 / 6.0.3 / 6.1.1（C2） | 无 | 无 | 16 | 无 |
| 6.0 / 6.0.3 / 6.1.1（ESP32） | 无 | 无 | 32 | 无 |
| 6.3-dev（C5/C6） | 无 | 无 | 32 | 16 |

`v5.3` 没有 ESP32-C5（C5 从 5.4 起）。`v6.0` 是 6.0 系第一个 tag，此时 `SOC_*` 已经消失。
作者「6.0 变了」「5.x 不变」两点都成立。

### 4.2 分支评估（head 与 base 对照）

| 配置 | head | base |
| --- | --- | --- |
| C6 / 6.0.3 | HP 32、LP 16 | HP 32、**LP 32** |
| P4 / 6.0.3（2 个 HP 端口） | port0,1 = 32、LP(port2) 16 | — |
| C2 / 6.0.3 | 16 | **32** |
| C6 / 5.5.4 | HP 32、LP 16 | HP 32、LP 16 |
| ESP32 / 5.5.4 | 32 | 32 |

head 与真实头文件取值一致；base 如报告所述对 LP 与 C2 返回 32。5.x 配置下两者完全相同。

### 4.3 写入分块

| 条件 | 最大单块 | 超过硬件深度 |
| --- | --- | --- |
| base，LP(hw 16)，9~97 B | 32（32 B 时） | 81 种 |
| head，LP(hw 16)，9~97 B | 16 | 0 |
| base，C2(hw 16)，33~97 B | 32 | 65 种 |
| head，C2(hw 16)，33~97 B | 16 | 0 |

`txfifo_limit` 仍为 32 时，17 字节起首块就超过 16，与作者「C5/C6 从 18 字节、P4 从 17 字节
开始失败」的边界吻合（C5/C6 的 17 字节能通过，应是硬件容忍了这 1 字节，只能在实机确认）。
改成 16 后 9~97 字节全部 ≤16 分块，总长不变。

### 4.4 CI

`IDFBuild.yml` 的 6.x 作业只有 `esp32` / `esp32s3`（6.0.2）；C5（5.5.2）、C6（5.4.3）、
P4（5.4.3）、C61（5.5.2）全在 5.x。`ArduinoBuild.yml` 里 C6/P4 是 3.1.3、C5 是 3.3.0
（基于 ESP-IDF 5.5.0），也没有 6.x。因此 **本 PR 新增的 `#elif` 在 CI 里一次都没有被
编译过**（`esp32` 没有 LP 端口，`I2C_LL_FIFO_LEN` 也是 32，所以只走到 HP 那条）。

## 5. 影响面与兼容性

- 取值与 5.x 相同（LP 16、C2 16、其余 32），6.x 只是回到 5.x 的分块方式。读取在 LP 上也会
  按 16 字节分块，但 5.x 的 LP 本来就是 16，I2C 读取拆成多条命令仍是同一次传输。
- 5.3~5.5 下新增的 `#elif` 是死代码；`__has_include` 的 include 逻辑未变。
- 没有 LP 端口的芯片（ESP32/S2/S3/C2/C3/H2/C61 等）走 `(void)i2c_port;`，不会产生未使用
  参数告警（`-Werror` 已确认）。

## 6. 风险与建议（均为非阻塞）

1. **CI 覆盖**：把 `esp32c6`（或 `esp32p4`）加到 6.0.2，把 `esp32c2` 也加到 6.0.2，新增的
   LP 分支与 HP 16 分支就都会进入编译。这不保证取值正确，但下次改名导致构建失败时能发现。
2. **静默回退**：有 LP 端口但 `SOC_LP_I2C_FIFO_LEN` 与 `I2C_LL_LP_FIFO_LEN` 都不存在时，
   会落进 `#else` 返回 HP 深度——正是本 PR 修掉的那类错误。把 `#if LGFX_LP_I2C_NUM > 0`
   里面的兜底改成 `#error`，可以防止将来改名后静默退回。现行 5.4~6.3-dev 组合都不会到达。

## 7. 未覆盖项与局限

- hardware `NOT RUN`：无实机；作者的 NFC 检测与 181/181 未复现。
- virtual-device `NOT RUN`：没有 6.x 编译链，且 5.x 下 base 与 head 二进制相同；Device
  Service 的 C6/P4 profile 也未见能观测 LP I2C FIFO 溢出的模型。
- C2 只有头文件取值与分支评估。
- 作者的 5.4.4 / 5.5.4 / 6.0.3 / 6.1 原生构建未重跑。

## 8. 回滚

未改动上游。库侧回退只需 revert `common.inl` 的那 5 行；5.x 行为不变，实际只会让 6.x 的
LP 与 C2 回到旧行为。

## 9. 重建

```bash
git clone https://github.com/m5stack/M5GFX /tmp/m5gfx
cd /tmp/m5gfx && git fetch origin develop && git fetch origin pull/432/head:pr432
bash <record>/code/probe-macros.sh                        # 头文件宏表
bash <record>/code/run.sh /tmp/m5gfx 452c15b pr432        # 抽取函数 + 分块算术
git checkout -q 452c15b
git apply --check <record>/patches/0001-i2c-idf6-fifo-len.patch
```
