# M5GFX #429: `Panel_CVBS.inl` 跟随 ESP-IDF 6.1.1 的 DAC LL 改名（构建验证）

- 日期：`2026-11-17`
- 结果：`PARTIAL`（构建层面已验证；硬件 / 虚拟设备的 CVBS 输出 `NOT RUN`）
- 工作类型：`pr`
- 条目：[m5stack/M5GFX#429](https://github.com/m5stack/M5GFX/pull/429)
  「Panel_CVBS: build with the DAC LL functions renamed in ESP-IDF 6.1.1」，作者 ainyan03，英文，OPEN
- 源码：PR head `2328ff8605f6cd25a32615122ee139927b64b28a`，base `develop`
  `ce73a4deb28854d7fc2ba0a2361792355dbd6b9f`
- 环境：macOS arm64；`espressif/idf:v6.1.1`；`esp32` 目标；最小 IDF 工程把 M5GFX 作为组件编译

## 结论

1. base 在 6.1.1 下复现 issue #425 的 5 条错误；PR head 同工程构建完成
   （1057 步，`m5gfx425.bin` 312,272 B，SHA-256 `7419b097…d1381d`）。
2. `__has_include(<hal/dac_types_private.h>)` 的判定与作者描述一致：该头只在 6.1.1 与 master 存在，
   5.1.6 / 5.2.8 / 5.4.3 / 6.0.2 / 6.1 / v5.5 的完整源码树里都没有。
3. 语义等价：`pad_power_on/off`、`sync_by_adc` 的寄存器写与旧函数相同；旧
   `digi_enable_dma` 的 `dac_dig_force` + `dac_clk_inv` 由 `pad_set_data_source` +
   `dma_clk_inv` 覆盖。唯一差别是 DIRECT 会清该通道 `dac_cw_en`（CVBS 不用余弦发生器），
   作者已在 diff 中注明。
4. 无阻塞问题。可选建议：CI 的 esp32 矩阵没有 6.1.x job，而改名发生在 6.1.1 补丁版本，
   建议加 `esp32` + `6.1.1`。

## 关键证据

- `evidence/base-errors.txt`：base `ce73a4d` + 6.1.1 的 5 条错误（行号 1976/1978/2037/2039/2040）。
- `evidence/build-base-ce73a4d-idf611-esp32.log`：未打补丁的完整构建日志（失败）。
- `evidence/build-patched-pr429-idf611-esp32.log`：PR head 的完整构建日志（`Project build complete`）。
- `evidence/patched-build-artifact.txt`：产物大小与 SHA-256。
- `evidence/gate-header-presence.txt`：各 IDF tag 是否存在 `hal/dac_types_private.h`（完整 tree API）。
- `evidence/idf-dac-ll-diff.txt`：6.1 / 6.1.1 的函数体对照与 IDF 自带驱动的调用顺序。
- `evidence/build-commands.txt`：可重建的命令。
- `patches/0001-panel-cvbs-idf611-dac-ll.patch`：PR head 的提交（`git format-patch`）。
- 已发布回复：见下方“已发布回复”。

## 未覆盖项

- hardware validation：`NOT RUN`，没有实机 CVBS 采集。
- virtual-device validation：`NOT RUN`，Device Service 的 esp32-lx6 机型没有 DAC→CVBS 模型与采集通道。
- Arduino-ESP32 各 core：未单独构建（PR CI 已覆盖 2.0.17 / 3.1.3 的 esp32，均为 pass）。
- 6.1 / 6.0.2 的实构建：未跑；旧分支与现状逐字相同，且 6.1 无该头文件。
