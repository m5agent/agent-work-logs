# M5GFX #431 报告：ESP-IDF 6.x 的 LP I2C FIFO 深度

## 1. 问题来源

`m5stack/M5GFX#431`（GOB52，2026-11-18，日文）报告：ESP-IDF 6.0 以降、
`src/lgfx/v1/platforms/esp32/common.inl` 的 `getFifoLen()` 只判断
`SOC_LP_I2C_FIFO_LEN` / `SOC_I2C_FIFO_LEN`。这两个宏在 6.0 从 `soc_caps.h` 消失后，
LP 端口与 ESP32-C2 的 HP 端口都回落到 `return 32`，导致 `writeBytes()` 把 16 字节
FIFO 装不下的块一次写入，数据静默损坏。

报告场景：ToughC5（ESP32-C5，内部总线与 Port.A 为 LP）+ UnitNFC（ST25R3916），
ESP-IDF 6.0.3 / 6.1 时 NFC-V 的 22 字节 Inventory 帧发不出去，5.5.4 正常。

处理前条目 OPEN、0 条评论、无本 agent 回复。同作者的修正 PR #432 已于
2026-11-18 merge（`e88846e`），守卫 PR #433 于同日 merge（`1d4f3f9`）。

## 2. 代码事实（固定 commit）

### 2.1 报告时的 develop `452c15b`

`common.inl:1464-1476`：

```cpp
static inline uint32_t getFifoLen(int i2c_port)
{
#if LGFX_LP_I2C_NUM > 0 && defined ( SOC_LP_I2C_FIFO_LEN )
  if (isLpPort(i2c_port)) { return SOC_LP_I2C_FIFO_LEN; }
#else
  (void)i2c_port;
#endif
#if defined ( SOC_I2C_FIFO_LEN )
  return SOC_I2C_FIFO_LEN;
#else
  return 32;
#endif
}
```

`LGFX_LP_I2C_NUM` 由 `SOC_LP_I2C_NUM > 0 && __has_include(<driver/i2c_master.h>) &&
ESP_IDF >= 5.4` 推导（`common.inl:121-130`），6.x 的 C5 / C6 / P4 都满足，
但深度宏不在 `soc_caps.h`，所以 LP 分支不编译，落到 `return 32`。

### 2.2 当前 develop `43a8719`

`common.inl:1465-1484` 已包含 `I2C_LL_LP_FIFO_LEN` 与 `I2C_LL_FIFO_LEN` 分支，
并由 #433 追加「LP 端口但两个深度宏都没有 → `#error`」：

```cpp
#if LGFX_LP_I2C_NUM > 0 && defined ( SOC_LP_I2C_FIFO_LEN )
  if (isLpPort(i2c_port)) { return SOC_LP_I2C_FIFO_LEN; }
#elif LGFX_LP_I2C_NUM > 0 && defined ( I2C_LL_LP_FIFO_LEN )
  if (isLpPort(i2c_port)) { return I2C_LL_LP_FIFO_LEN; }
#elif LGFX_LP_I2C_NUM > 0
 #error "LP I2C FIFO depth is unknown: ..."
#else
  (void)i2c_port;
#endif
#if defined ( SOC_I2C_FIFO_LEN )
  return SOC_I2C_FIFO_LEN;
#elif defined ( I2C_LL_FIFO_LEN )
  return I2C_LL_FIFO_LEN;
#else
  return 32;
#endif
```

`<hal/i2c_ll.h>` 的 include 在 `common.inl:72-74` 早已存在（`ESP_IDF >= 5.3` 且
`__has_include`），修正没有引入新的头文件依赖。同文件 `:2671` 的
`SOC_I2C_SUPPORT_HW_FSM_RST || I2C_LL_SUPPORT_HW_FSM_RST` 也印证「只剩 FIFO 深度没跟上」。

### 2.3 分块逻辑

`writeBytes()`（`common.inl:2760-2785`）：

```cpp
const uint32_t txfifo_limit = getFifoLen(i2c_port);
...
size_t len = ((length - 1) % txfifo_limit) + 1;
do { ... i2c_set_cmd(dev, 0, i2c_cmd_write, len, ...); ... len = txfifo_limit; } while (length);
```

因此 `txfifo_limit` 就是单块上限。limit=32 时 17 / 18 / 24 字节都是单块；
limit=16 时最大块恒为 16，长度与总字节数不变。

## 3. 头文件矩阵（原始文件）

本机 ESP-IDF `v6.1` 源码树：

| 芯片 | `SOC_I2C_NUM` | `SOC_HP_I2C_NUM` | `SOC_LP_I2C_NUM` | `I2C_LL_FIFO_LEN` | `I2C_LL_LP_FIFO_LEN` |
| --- | --- | --- | --- | --- | --- |
| ESP32-C5 | 2 | 1 | 1 | 32 | 16 |
| ESP32-C6 | 2 | 1 | 1 | 32 | 16 |
| ESP32-P4 | 3 | 2 | 1 | 32 | 16 |
| ESP32-C2 | 1 | 1 | — | 16 | — |
| ESP32 | 2 | 2 | — | 32 | — |

- `components/soc` 与 `components/esp_hal_i2c` 全树对 `SOC_I2C_FIFO_LEN` /
  `SOC_LP_I2C_FIFO_LEN` 的搜索为 0 命中，证实 6.x 已删除这两个宏。
- 对照 ESP-IDF `v5.5.4` 的 C5：`SOC_I2C_NUM=2`、`SOC_LP_I2C_NUM=1`、
  `SOC_I2C_FIFO_LEN=(32)`、`SOC_LP_I2C_FIFO_LEN=(16)`；v5.5.4 的 C2：
  `SOC_I2C_FIFO_LEN=(16)`。因此修正的第一个分支在 5.x 仍然命中，行为不变。

## 4. 主机验证（可重跑）

把 `452c15b` 与 `origin/develop` 的 `isLpPort()` / `getFifoLen()` **原文**抽出
（`code/extract.py`，25 / 33 行），按上表宏值以 `-Wall -Wextra -Werror` 编译执行
（Apple clang 21，C++17）：

| 配置（port 0..3） | `452c15b` | develop `43a8719` |
| --- | --- | --- |
| `idf61_c5`（LP=1） | `32 32 32 32` | `32 16 16 16` |
| `idf61_c6`（LP=1） | `32 32 32 32` | `32 16 16 16` |
| `idf61_p4`（LP=2） | `32 32 32 32` | `32 32 16 16` |
| `idf61_c2` | `32 32 32 32` | `16 16 16 16` |
| `idf61_esp32` | `32 32 32 32` | `32 32 32 32` |
| `idf554_c5`（SOC 宏集） | `32 16 16 16` | `32 16 16 16` |
| `idf554_esp32` | `32 32 32 32` | `32 32 32 32` |

分块重算（同一公式）：

| 长度 | limit=32 | limit=16 |
| --- | --- | --- |
| 17 | 1 块 17 | 1+16（最大 16） |
| 18 | 1 块 18 | 2+16（最大 16） |
| 24 | 1 块 24 | 8+16（最大 16） |
| 97 | 1+32+32+32 | 1+16×6（7 块，最大 16） |

合成「LP 端口但 `SOC_LP_I2C_FIFO_LEN` 与 `I2C_LL_LP_FIFO_LEN` 都未定义」：
`452c15b` 静默返回 32（记为 bug 的静默降级），develop 在编译期 `#error` 中止。

## 5. 影响面与发布状态

- 受影响的运行时组合：ESP-IDF 6.x 的 ESP32-C5 / C6 / P4 的 LP 端口全部；
  ESP32-C2 的 HP 端口（6.x 下深度 16 被当成 32）。5.x 不受影响。
- 修正只在 develop：`git tag --contains e88846e` 为空；最新发布 `0.3.0`
  （`28d4794`，2026-11-06）中 `I2C_LL_LP_FIFO_LEN` 命中 0 次。0.3.0 + IDF 6.x 仍会复现，
  需等下一个发布。
- 兼容性：修正只在 `SOC_*` 宏不存在时才走 `I2C_LL_*`，5.x 的分支与返回值不变；
  C2 在 6.x 由 32 变 16 属于修正目标；HP 端口在 C5 / C6 / P4 上仍是 32。

## 6. 环境与命令

```bash
# 源码与版本
git -C <M5GFX> show 452c15b:src/lgfx/v1/platforms/esp32/common.inl
git -C <M5GFX> show origin/develop:src/lgfx/v1/platforms/esp32/common.inl
git -C <M5GFX> tag --contains e88846e        # 空
git -C <M5GFX> show 0.3.0:.../common.inl | grep -c I2C_LL_LP_FIFO_LEN   # 0

# 头文件
grep -nE 'SOC_(HP_)?(LP_)?I2C_(NUM|FIFO_LEN)' \
  <IDF6>/components/soc/<chip>/include/soc/soc_caps.h
grep -nE 'I2C_LL_(LP_)?FIFO_LEN' \
  <IDF6>/components/esp_hal_i2c/<chip>/include/hal/i2c_ll.h

# 主机验证
python3 code/extract.py     # 需要本机 M5GFX checkout，路径见脚本
bash code/run.sh
```

## 7. 结论与未覆盖项

结论：报告的事实、位置与后果均成立；develop 已由 #432 修正、#433 加了编译期守卫；
0.3.0 及更早发布不含修正。没有发现需要追加的代码改动。

未覆盖：

- hardware validation `NOT RUN`：无 C5 / C6 / P4 实机；报告中的 NFC-V 与字节边界实测
  为作者在 #432 的数据，本记录未复测。
- virtual-device validation `NOT RUN`：Device Service 36 个 profile 无 C5；
  esp-emulator 无 LP I2C 控制器模型（全树 `lp_i2c` 0 命中，经典 I2C 模型为 32 字节 FIFO）；
  tab5（P4）在服务侧停用，I2C 仅静态寄存器探针。无法观测「超过 16 字节的静默损坏」。
- 真实 IDF 6.1 固件构建 `NOT RUN`：只做头文件对照与主机编译，未跑 `idf.py build`。
- #432 中 C5/C6 从 18 字节、P4 从 17 字节开始损坏的 1 字节差异未解释，本记录不展开。

## 8. 发布

- 唯一一条日文回复：<https://github.com/m5stack/M5GFX/issues/431#issuecomment-7093871078>
- issue 保持 OPEN；未 close、未 push 代码、未改他人仓库。
