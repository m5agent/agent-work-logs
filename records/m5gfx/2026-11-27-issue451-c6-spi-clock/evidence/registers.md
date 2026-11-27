# 寄存器读回与换算（nesso-n1 / ESP32-C6 / esp32sim）

sketch 直接读 `PCR_SPI2_CLKM_CONF_REG`（C6: `DR_REG_PCR_BASE + 0xc4`，bit[21:20] 为
`spi2_clkm_sel`）与 SPI2 的 `clock` 寄存器（`clkcnt_n` bit[17:12]、`clkdiv_pre` bit[21:18]、
`clk_equ_sysclk` bit[31]）。

换算：`div = (clkdiv_pre + 1) * (clkcnt_n + 1)`；`sclk = source / div`，
source = XTAL 40 MHz（sel=0）或 PLL_F80M 80 MHz（sel=1）。

原始行（`evidence/serial-esp32sim.txt`）：

```
boot pcr_clkm=0x00000000 sel=0 clk_equ_sysclk=0 clkcnt_n=0 clkdiv_pre=0 div=1 src=40000000 sclk=40000000
arduino_only_8MHz pcr_clkm=0x00000000 sel=0 clk_equ_sysclk=0 clkcnt_n=4 clkdiv_pre=0 div=5 src=40000000 sclk=8000000
m5gfx_bus_init=1
after_m5gfx_bus_init pcr_clkm=0x00500000 sel=1 clk_equ_sysclk=0 clkcnt_n=4 clkdiv_pre=0 div=5 src=80000000 sclk=16000000
arduino_after_m5gfx_8MHz pcr_clkm=0x00500000 sel=1 clk_equ_sysclk=0 clkcnt_n=4 clkdiv_pre=0 div=5 src=80000000 sclk=16000000
arduino_after_m5gfx_2MHz pcr_clkm=0x00500000 sel=1 clk_equ_sysclk=0 clkcnt_n=1 clkdiv_pre=9 div=20 src=80000000 sclk=4000000
done
```

说明：

- `0x00500000` = bit21:20 = `01`，即 PLL_F80M；该值只在 M5GFX 总线初始化之后出现。
- Arduino 单独运行时 sel=0、8 MHz 请求得到 div=5（40/5=8 MHz），说明同一读回路径能反映真实选择。
- M5GFX 初始化后的 8 MHz、2 MHz 两次 `beginTransaction` 都没有把 sel 改回 0；分周仍是按 40 MHz 源计算，
  在 80 MHz 源下正好是请求值的 2 倍。
- 虚拟设备不模拟 SPI 时钟频率，因此 `sclk` 是按 SoC 时钟树从寄存器换算的值，不是引脚测量。
