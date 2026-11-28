# SCLK 换算方式

两份 sketch 都不测量物理引脚，只读取寄存器：

- `PCR_SPI2_CLKM_CONF_REG`（C6 `pcr_reg.h`，`DR_REG_PCR_BASE + 0xc4`）：
  - `PCR_SPI2_CLKM_SEL`：bitpos [21:20]，`0` = XTAL，`1` = PLL_F80M，`2` = FOSC；
  - `PCR_SPI2_CLKM_EN`：bit 22，IDF 总线初始化后置 1，本 PR 的读改写会保留它。
- SPI2 `clock` 寄存器：
  - `clk_equ_sysclk=1` 时分周为 1；
  - 否则 `div = (clkdiv_pre + 1) * (clkcnt_n + 1)`；
  - `SCLK = 源频率 / div`。

C6 上 `get_xtal_frequency()` 为 40 MHz，PLL_F80M 为 80 MHz；因此：

| 阶段 | `pcr_clkm` | sel | 源 | 分周 | 推定 SCLK |
| --- | --- | --- | --- | --- | --- |
| base：M5GFX 初始化后 | `0x00500000` | 1 | 80 MHz | 5 | 16 MHz |
| base：Arduino 8 MHz 请求 | `0x00500000` | 1 | 80 MHz | 5 | 16 MHz |
| base：Arduino 2 MHz 请求 | `0x00500000` | 1 | 80 MHz | 20 | 4 MHz |
| head：M5GFX 初始化后 | `0x00400000` | 0 | 40 MHz | 5 | 8 MHz |
| head：Arduino 8 MHz 请求 | `0x00400000` | 0 | 40 MHz | 5 | 8 MHz |
| head：Arduino 2 MHz 请求 | `0x00400000` | 0 | 40 MHz | 20 | 2 MHz |
| head：显示写入 40 MHz | `0x00400000` | 0 | 40 MHz | 1（`clk_equ_sysclk=1`） | 40 MHz |

边界：`esp32sim` 的 GP-SPI 模型只处理寄存器与传输完成，不建模 SCLK 周期；上表是按
mux/分周寄存器换算的值，不是示波器或逻辑分析仪测量。
