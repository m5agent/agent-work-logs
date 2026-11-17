# 报告：M5GFX #429 `Panel_CVBS.inl` 跟随 ESP-IDF 6.1.1 的 DAC LL 改名

## 1. 对象与背景

`m5stack/M5GFX#429` 是作者 ainyan03 针对 issue #425 的修正 PR。ESP-IDF 6.1.1 的
commit `3e279c2a1df`（"refactor(dac): rename LL APIs and introduce sintx manager"）把
`Panel_CVBS.inl` 使用的 DAC LL 函数改名，并删除 `dac_ll_digi_enable_dma()`：
`Panel_CVBS.inl` 参与所有 esp32 构建（`lgfx_v1_platforms.cpp` 无条件包含，文件内
`CONFIG_IDF_TARGET_ESP32` 为界），所以整个库在 `esp32` + 6.1.1 下无法编译。

| 6.1 及以前 | 6.1.1 |
| --- | --- |
| `dac_ll_power_on` / `dac_ll_power_down` | `dac_ll_pad_power_on` / `dac_ll_pad_power_down` |
| `dac_ll_rtc_sync_by_adc` | `dac_ll_sync_by_adc` |
| `dac_ll_digi_enable_dma(en)`（写 `dac_dig_force` 与 `dac_clk_inv`） | `dac_ll_pad_set_data_source(ch, DMA/DIRECT)` + `dac_ll_dma_clk_inv(en)` |

PR head `2328ff8605f6cd25a32615122ee139927b64b28a`（单提交），base `develop`
`ce73a4deb28854d7fc2ba0a2361792355dbd6b9f`（#427 合并后的先端）。

## 2. 结论

1. 补丁有效：base `ce73a4d` 在 `espressif/idf:v6.1.1`、`esp32` 下复现 issue #425 的 5 条错误
   （`Panel_CVBS.inl:1976`、`1978`、`2037`、`2039`、`2040`）；同一工程换成 PR head 后
   1057 步构建完成，产出 `m5gfx425.bin` 312,272 字节，
   SHA-256 `7419b09762673354ff2dd39cb5eff253c79d7b5d8bdfec4173af306142d1381d`。
2. 选择方式（`__has_include(<hal/dac_types_private.h>)`）与作者描述一致：该头文件是 6.1.1 随改名
   一起引入的 `components/esp_hal_ana_conv/include/hal/dac_types_private.h`，被 6.1.1 的
   `esp32/dac_ll.h` 自身包含。逐一核对完整源码树（GitHub trees API，`truncated=false`）：
   5.1.6、5.2.8、5.4.3、6.0.2、6.1、release/v5.5 均无此头文件，6.1.1 与 master 有。
   因此旧版本走旧分支，分支内容与现状逐字相同，不引入新风险。
3. 语义等价：`dac_ll_pad_power_on/off`、`dac_ll_sync_by_adc` 的寄存器写与 6.1 的旧函数逐行相同；
   旧 `dac_ll_digi_enable_dma(en)` 等价于「数据源选择 + `dac_ll_dma_clk_inv(en)`」。
   唯一差别是停止时选 `DAC_DATA_SOURCE_DIRECT` 会顺带清掉该通道的 `dac_cw_en`（余弦发生器），
   CVBS 不使用余弦发生器，作者已在 diff 注释中写明。IDF 自带 DAC 驱动正是同一组调用
   （`esp_driver_dac/esp32/dac_dma.c:152/193` 的 `dac_ll_dma_clk_inv`，
   `dac_common.c:76-78` 的 `set_data_source` + `sync_by_adc(false)` + `pad_power_on`）。
4. 未发现阻塞问题。可选建议：CI 的 esp32 矩阵只有 5.1.6 / 5.4.3 / 6.0.2（`IDFBuild.yml`），
   6.1.x 没有任何 esp32 job，而改名恰好发生在 6.1.1 这个补丁版本，所以当时的绿 CI 不会覆盖。
   增加一条 `esp32` + `6.1.1` 的构建项可以直接锁住这条路径。

## 3. 环境与命令

- 主机：macOS arm64。
- 镜像：`espressif/idf:v6.1.1`（本地已有），IDF 6.1.1，xtensa-esp32-elf-g++ 15.2.0。
- 工程：#425 用过的极小 IDF 工程（`main` 仅 `#include "M5GFX.h"` 并实例化 `M5GFX`，
  `REQUIRES M5GFX`，M5GFX 源码放在 `components/M5GFX`）。组件会编译全部库源码，
  与 CI 的 `examples/Test/build_test` 覆盖的是同一个 `lgfx_v1.cpp` 翻译单元。
- 两次构建仅 M5GFX 源码不同：

```bash
git -C M5GFX archive ce73a4d | tar -x -C proj-base/components/M5GFX   # 未打补丁
git -C M5GFX archive pr429  | tar -x -C proj-pr/components/M5GFX      # PR head
docker run --rm -v $PWD/proj-pr:/project -w /project espressif/idf:v6.1.1 \
  bash -lc 'source /opt/esp/idf/export.sh; idf.py set-target esp32; idf.py build'
```

## 4. 结果

| 检查 | 结果 |
| --- | --- |
| base `ce73a4d` + 6.1.1 / esp32 | 失败，5 条 `error:`，行号 1976/1978/2037/2039/2040，与 issue #425 完全一致 |
| PR head + 6.1.1 / esp32 | 成功，`Project build complete`，1057 步，`m5gfx425.bin` 312,272 B |
| `__has_include` 判定表 | 5.1.6 / 5.2.8 / 5.4.3 / 6.0.2 / 6.1 / v5.5 无该头；6.1.1 / master 有 |
| 旧分支等价性 | `< 6.1.1` 分支的调用与 `develop` 现状逐字相同（仅换了排列顺序） |
| 6.1 + PR head | 见第 6 节（若未执行则标注 NOT RUN） |

## 5. 影响面

- 只改 `Panel_CVBS.inl`，esp32 之外的目标根本不编译该文件（`CONFIG_IDF_TARGET_ESP32` 保护）。
- 6.1.1 之前的 SDK 走 `#else`，与当前代码等价（`dac_ll_digi_enable_dma(false)` 后 `power_down` /
  循环内 `power_on` 后 `rtc_sync_by_adc` + `digi_enable_dma(true)`）。
- Arduino-ESP32（IDF 5.x）走旧分支；但 Arduino 路径本次没有单独构建验证。

## 6. 未覆盖项

- **hardware validation：NOT RUN**。没有在真实 ESP32 上采集 CVBS 画面；PR 也只证明了编译链接。
- **virtual-device validation：NOT RUN**。Device Service 的 esp32-lx6 机型（core2、stickc-plus2、
  basic-v27 等）都只有 LCD/按键/串口模型，没有 DAC→CVBS 输出模型，也没有 CVBS 采集通道；
  该回归本身是编译期 API 改名，运行时不可观测。
- **Arduino-ESP32 各 core 版本**：只做了头文件存在性判断，未构建。
- **6.1 / 6.0.2 的实构建**：6.1 的 `< 6.1.1` 分支保持原样，且 6.1 头文件已确认无
  `dac_types_private.h`，未另跑一次完整构建。
- `dac_ll_pad_set_data_source` 清 `dac_cw_en` 的实际影响：CVBS 不用余弦发生器，未做运行时确认。
- CI 是否接受新增 6.1.1 job：只是建议，未改工作流。
