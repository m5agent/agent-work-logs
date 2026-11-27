# M5GFX Issue #451（ESP32-C6: M5GFX 初始化后 Arduino SPI 时钟翻倍）虚拟设备复现

- 日期：`2026-11-27`
- 结果：`PARTIAL`（寄存器级因果链已在虚拟设备复现；SCLK 波形与实机 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/M5GFX/issues/451
- 源码版本：`m5stack/M5GFX @ 603092aab60e32fadd1d73abd472068a35e189e8`（develop，`0.3.0-103-g603092a`）；对照 `0.3.0` 同区域逐行一致（行号偏移 +117）
- 环境：macOS arm64；Arduino-ESP32 `3.3.13`（`esp32-hal-spi.c` 与报告者所用 `3.3.12` 逐字节一致）；本机 Device Service 的 `nesso-n1`（ESP32-C6，ST7789/SPI2）`esp32sim` profile

## 结论

报告的现象与根因链在虚拟设备上成立：M5GFX 的 SPI 总线初始化会先 `SPI.end()/SPI.begin()`，再调用
`spi_bus_initialize()`；ESP-IDF 5.5.5 的 `spi_ll_master_init()` 在 C6 上把 `PCR.spi2_clkm_sel`
写成 `1`（PLL_F80M），而 Arduino 的分周计算仍以 XTAL 40 MHz 为源。实测寄存器状态：

| 阶段 | `PCR_SPI2_CLKM_CONF` | sel | 分周 | 源 | 推定 SCLK |
| --- | --- | --- | --- | --- | --- |
| Arduino 单独 `SPI.begin()` + 8 MHz | `0x00000000` | 0 (XTAL) | 5 | 40 MHz | 8 MHz |
| M5GFX `Bus_SPI::init()` 之后 | `0x00500000` | 1 (PLL_F80M) | 5 | 80 MHz | 16 MHz |
| 再 `SPI.beginTransaction(8 MHz)` | `0x00500000` | 1 | 5 | 80 MHz | 16 MHz（请求的 2 倍） |
| 再 `SPI.beginTransaction(2 MHz)` | `0x00500000` | 1 | 20 | 80 MHz | 4 MHz（请求的 2 倍） |

同时确认报告中的三点源码事实：`spi::init()` 调用 `SPI.end()/SPI.begin()` 后再 `spi_bus_initialize()`
（develop `common.inl:1037-1038`、`:1082`）；Arduino 的 `spiSourceFrequency()` 取的是 XTAL 标称频率、
不读 mux（`esp32-hal-spi.c:703-720`）；`SPI.begin()` 二次调用直接返回（`SPI.cpp:67`）。

## 关键证据

- 构建：`arduino-cli 1.6.0` + `esp32:esp32 3.3.13` + M5GFX `603092a`，merged image SHA256
  `df4a4e087708588204c3da5ef99ee290c54a14dfe894d0a991afe4347b1f62c1`（16 MiB）
- 运行：`nesso-n1` / `esp32sim`，串口原始输出 `evidence/serial-esp32sim.txt`
- 源码核对：`evidence/registers.md`、`report.md` 的“代码位置”节
- 复现工程：`code/nesso_spi_repro/nesso_spi_repro.ino`

## 文件

- `report.md`：完整报告（含 IDF 5.5.5 各目标 `master_init` 的差异）
- `run.json`：结构化记录
- `evidence/serial-esp32sim.txt`：虚拟设备控制台原始输出
- `evidence/build.log`：工具链、构建命令与产物哈希
- `evidence/registers.md`：寄存器读回与换算
- `code/nesso_spi_repro/`：最小复现 sketch

## 未覆盖项

- 未测 SCLK 引脚波形：`esp32sim` 的 GP-SPI 模型不建模时钟频率，本文的 SCLK 由 PCR mux 与分周寄存器换算。
- 实机 `NOT RUN`：本机没有 C6 实机；报告者的实机观测（8 MHz 时 SX1262 读取异常、2 MHz 正常）未复验。
- `C5 / C61 / H2 / P4` 未运行；仅对 IDF 5.5.5 源码做了对照（C61 同样写 `sel=1`，H2 写 `0`，C5 的
  `master_init` 不改 mux，P4 走另一套 Arduino 分周/选源逻辑）。
- 报告者的修复方案（`spi_bus_initialize()` 后写回 mux）未实现、未验证。
