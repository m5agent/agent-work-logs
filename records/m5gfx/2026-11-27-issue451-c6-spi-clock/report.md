# M5GFX Issue #451：ESP32-C6 上 M5GFX 初始化后 Arduino SPI 以请求的 2 倍时钟运行

## 1. 问题与复现目标

报告者 GOB52 在 M5Stack Unit C6L（SSD1306/SPI2）与 Arduino Nesso N1（ST7789/SPI2）上观察到：
`M5.begin()` 之后，用 Arduino `SPI` 驱动同一 host 上的 SX1262 时，`SPISettings(8000000, …)`
实际输出约 16 MHz，2 MHz 实际约 4 MHz；8 MHz 下 RadioLib 的 `GetPacketType` 异常、`begin()`
返回 -20。两种情况（C6L、Nesso N1）都是 LoRa 芯片与显示屏共用 SCK/MOSI/MISO（GPIO20/21/22）。

本次目标：在可用证据层级中复现“M5GFX 初始化改变了 SPI2 的时钟源，而 Arduino 的分周仍按 XTAL 计算”
这一因果链，并核对报告中的源码结论与修复范围。

## 2. 假设与根因

假设（来自报告者，逐条核验）：

1. `lgfx::v1::spi::init()` 在 Arduino 路径上先 `SPI.end(); SPI.begin(sclk, miso, mosi);`，
   Arduino 的 `spiStartBus()` 把 SPI2 时钟源固定到 XTAL，`spi_ll_set_clk_source(..., SPI_CLK_SRC_XTAL)`
   写 `PCR.spi2_clkm_sel = 0`。
2. 同一个 `spi::init()` 随后调用 ESP-IDF 的 `spi_bus_initialize()`，其 `spi_ll_master_init()` 在 C6 上
   无条件写 `PCR.spi2_clkm_conf.spi2_clkm_sel = 1`（PLL_F80M）。
3. Arduino 的 `spiSourceFrequency()` 返回的是 `SPI_CLK_SRC_XTAL` 的标称频率（40 MHz），它按枚举值
   取频率，不读 PCR 的 mux；`SPI.begin()` 第二次调用直接 `return true`（`SPI.cpp:67`），不会重新
   `spiStartBus()` 把 mux 改回 XTAL。
4. 因此后续 `SPI.beginTransaction(SPISettings(f, …))` 用 40 MHz 源算分周，实际源是 80 MHz，
   输出即 2×f。

虚拟设备实测与假设一致（见第 4 节）。根因层次是 **Arduino-ESP32 与 ESP-IDF 对 SPI2 时钟源选择的
所有权冲突**，触发点是 M5GFX 在 Arduino 路径上混用两套 SPI 初始化。

补充核验：报告者给出的 `common.inl:920`（`SPI.end()`）与 `:965`（`spi_bus_initialize`）是
**0.3.0 tag 的行号**；develop `603092a` 的同一区域整体下移 117 行（`:1037`、`:1082`），代码本身
逐行一致。报告正文写“以下の行番号は develop のもの”与实际不符，回复中已中性指出。

## 3. 代码位置

M5GFX develop `603092aab60e32fadd1d73abd472068a35e189e8`：

- `src/lgfx/v1/platforms/esp32/common.inl:1037-1038`：`SPI.end(); SPI.begin(spi_sclk, spi_miso, spi_mosi);`
- `src/lgfx/v1/platforms/esp32/common.inl:1082`：`spi_bus_initialize(...)`
- `src/lgfx/v1/platforms/esp32/common.inl:1262`：`FreqToClockDiv(getSpiClockFrequency(spi_host), freq)`，
  即 M5GFX 自己每次事务都按当前 mux 重算分周
- `src/lgfx/v1/platforms/esp32/common.inl:460-490`：C6 的 `getSpiClockFrequency()`，`sel==0` 返回 XTAL，
  `sel==1` 返回 80 MHz

Arduino-ESP32 `3.3.13`（`esp32-hal-spi.c` 与 `3.3.12` 的 diff 为空）：

- `cores/esp32/esp32-hal-spi.c:703-720`：`spiSourceFrequency()` 按 `ARDUINO_SPI_CLK_SRC`
  （C6 为 `SPI_CLK_SRC_XTAL`）向时钟树要标称频率
- `cores/esp32/esp32-hal-spi.c:926-930`：`spiStartBus()` 里的 `spi_ll_set_clk_source(..., ARDUINO_SPI_CLK_SRC)`
- `cores/esp32/esp32-hal-spi.c:1952`：`spiFrequencyToClockDiv()` 使用 `spiSourceFrequency()`
- `libraries/SPI/src/SPI.cpp:63-69`：`begin()` 在 `_spi` 非空时直接返回
- `libraries/SPI/src/SPI.cpp:199-208`：`beginTransaction()` 只在频率或当前分周变化时重算，
  重算仍走 `spiFrequencyToClockDiv()`

ESP-IDF 5.5.5（`components/hal/*/include/hal/spi_ll.h`）：

- C6 `:188`：`spi_ll_master_init()` 写 `PCR.spi2_clkm_conf.spi2_clkm_sel = 1`
- C61 `:212`：同样写 `1`
- H2 `:189`：写 `0`（XTAL）
- C5 `:193` 起的 `spi_ll_master_init()`：不改 mux（选源只在 `spi_ll_set_clk_source()` 中发生）
- P4：ESP32-P4 走 `HP_SYS_CLKRST`，Arduino 的 `spiFrequencyToClockDiv()` 会同时评估 XTAL/SPLL 并
  在 `_spiSetClockDivInternal()` 里切源，与 C6 的路径不同

因此报告里“C5 / C6 / C61 / H2 / P4 都要在 `spi::init()` 里保存/恢复 mux”的范围偏宽：按 IDF 5.5.5
源码，C6 与 C61 的 `spi_ll_master_init()` 会把 mux 改成 PLL，H2 改回 XTAL，C5 不动 mux，P4 是另一套
逻辑。实际需要处理的范围应以各目标的 `spi_ll_master_init()`/`SPI_CLK_SRC_DEFAULT` 为准。

## 4. 构建与运行环境

- 主机：macOS arm64，`arduino-cli 1.6.0`
- 核心：`esp32:esp32 3.3.13`（报告者为 pioarduino 55.03.312-1 / 3.3.12；两者的
  `cores/esp32/esp32-hal-spi.c` 完全相同，`SPI.cpp` 的 `begin()` 早退也未变）
- 库：M5GFX `603092a`（develop），以 `--library` 指向本地 checkout
- 目标：`esp32:esp32:arduino_nesso_n1`（ESP32-C6，16 MB flash）
- 虚拟设备：Device Service 的 `nesso-n1` profile，`runtime=esp32sim`，该 profile 的显示为
  ST7789 135×240 / SPI2，与报告中的 Nesso N1 一致；Unit C6L 没有 profile，未使用

构建命令：

```
arduino-cli compile --fqbn esp32:esp32:arduino_nesso_n1 \
  --library <M5GFX checkout> --output-dir out nesso_spi_repro
```

产物：`nesso_spi_repro.ino.merged.bin`，SHA256
`df4a4e087708588204c3da5ef99ee290c54a14dfe894d0a991afe4347b1f62c1`，16 777 216 字节。

## 5. 执行过程与证据

sketch 不做面板初始化，直接调用 `lgfx::Bus_SPI::init()`——它与 `M5.begin()` 的显示路径一样进入
`spi::init()`，但避免把板级探测/面板时序引入结果。随后按报告的顺序用 Arduino `SPI` 发事务：

1. `SPI.begin(20, 22, 21)` + 8 MHz 事务（Arduino 单独运行基线）
2. M5GFX `Bus_SPI::init()`
3. `SPI.beginTransaction(8 MHz)` + 一次 `transfer`
4. `SPI.beginTransaction(2 MHz)` + 一次 `transfer`

每个阶段读回 `PCR_SPI2_CLKM_CONF_REG` 与 SPI2 `clock` 寄存器（原始串口见
`evidence/serial-esp32sim.txt`，换算见 `evidence/registers.md`）：

| 阶段 | sel | 分周 | 源 | 推定 SCLK |
| --- | --- | --- | --- | --- |
| boot | 0 | 1 | 40 MHz | 40 MHz |
| Arduino 单独 8 MHz | 0 | 5 | 40 MHz | 8 MHz |
| M5GFX 初始化后 | 1 | 5 | 80 MHz | 16 MHz |
| Arduino 8 MHz（M5GFX 后） | 1 | 5 | 80 MHz | 16 MHz |
| Arduino 2 MHz（M5GFX 后） | 1 | 20 | 80 MHz | 4 MHz |

`m5gfx_bus_init=1` 表示总线初始化成功；两条 8 MHz/2 MHz 事务执行后 sel 保持 1。基线一栏（Arduino
单独 8 MHz → 8 MHz）说明同一读回路径能够反映真实的 mux 选择，不是读数恒定值。

证据边界：`esp32sim` 的 GP-SPI 模型只处理寄存器与传输完成，不建模 SCLK 频率；表中的 SCLK 由
PCR mux（XTAL 40 MHz / PLL_F80M 80 MHz，C6 `pcr_struct.h` 中 `spi2_clkm_sel` 定义）与分周寄存器
换算，不是引脚测量。真实波形与“8 MHz 时 SX1262 读取异常”仍是报告者的实机观测，本次未复验。

## 6. 关于修复方向的观察（代码级，未验证）

报告的方案是“在 `spi_bus_initialize()` 前保存 mux，之后写回”。按代码，M5GFX 每次事务都用
`getSpiClockFrequency()` 重新读取 mux 并重算分周（`common.inl:1262`），所以把源改回 XTAL 不会让
M5GFX 的显示时序失效；但会改变显示读取的实际频率：请求 16 MHz、40 MHz 源只能取 div=3 →
13.33 MHz（80 MHz 源可取 div=5 → 16 MHz），与报告者的预期一致。另需确认写回 mux 后 IDF
`spi_device` 句柄内缓存的 source/分周假设是否仍成立（M5GFX 在 Arduino 路径上用裸寄存器发数据，
但 `spi_bus_add_device()` 仍会配置该句柄）。这两点都未在本次执行中验证。

## 7. 未覆盖项与风险

- SCLK 引脚波形未测量；虚拟设备不建模 SPI 时钟频率。
- 实机 `NOT RUN`：本机无 C6 实机；报告者的 8 MHz 失败/2 MHz 成功未复验。
- Unit C6L 无设备 profile；用同 SoC、同 ST7789/SPI2 的 Nesso N1 复现。
- C5 / C61 / H2 / P4 未运行，仅做 IDF 5.5.5 源码对照。
- 修复方案未实现、未验证；`SPI.end()` 后 IDF 句柄与 Arduino `_spi` 的生命周期问题未展开。
