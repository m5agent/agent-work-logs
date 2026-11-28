# M5GFX #452：恢复 Arduino SPI 时钟源（C6 SPI2）

- 日期：`2026-11-28`
- 结果：`PARTIAL`（`virtual-device validation` + `code-level verification` + build；
  真机、SCLK 波形、C5/C61/H2 运行时、`readRect` 读回为 `NOT RUN`）
- 工作类型：`pr-review`
- 条目：[m5stack/M5GFX#452](https://github.com/m5stack/M5GFX/pull/452)，作者 `ainyan03`，
  英文，OPEN；评审前 comments / reviews 均为 0
- 源码：PR head `e1666e9c175725b426a7aef9e4b17622f1d9813a`
  （base `603092aab60e32fadd1d73abd472068a35e189e8` = develop tip）；1 文件 +18/-0
- 环境：macOS arm64；`arduino-cli 1.6.0` + `esp32:esp32@3.3.13`（ESP-IDF 5.5.5）；
  本机 Device Service 的 `nesso-n1` profile（`runtime=esp32sim`，Arduino Nesso N1 /
  ESP32-C6 / ST7789 135×240 / SPI2 / 16 MB flash）

## 结论

修复在报告的 C6 + Arduino 路径上有效，未发现阻塞合并的问题：M5GFX 总线初始化后
`PCR.spi2_clkm_sel` 保持 0（XTAL 40 MHz），Arduino 8 MHz / 2 MHz 请求分别恢复为
8 MHz / 2 MHz（base 为 16 MHz / 4 MHz）。显示路径使用真实的 Nesso N1 面板参数，
40 MHz 写入正常，base 与 head 的画面 PNG 完全相同；16 MHz 读变为约 13.3 MHz，
与 PR 描述一致。

PR 描述里的 IDF 行为与源码核对一致：IDF 5.5.5 在 C6/C61 的
`spi_bus_add_device()` → `spi_master_init_driver()` → `spi_hal_init()` →
`spi_ll_master_init()` 中写 PLL；C5 不写，H2 写 XTAL；IDF 6.1 的
`spi_ll_master_init()` 已不写 mux，而 M5GFX 不用 IDF 的 `spi_device_transmit()`，
因此在 6.x 上写回同值。

## 关键证据

- 寄存器路径：base `603092a` 在 M5GFX 初始化后 `pcr_clkm=0x00500000`（sel=1，PLL_F80M），
  Arduino 8 MHz → div 5 → 16 MHz；head `e1666e9` 为 `0x00400000`（sel=0，XTAL 40 MHz），
  8 MHz → 8 MHz、2 MHz → 2 MHz。重复运行结果相同。
- 显示路径：head `display_init=1`、135×240，`clk_equ_sysclk=1` → 40 MHz；
  base 为 PLL/2 → 40 MHz。两版画面 PNG sha256 均为
  `b9db9630a017ab699f880893ff9946441345460389532682b9013c8ad40ff258`。
- 构建：Nesso N1 四个镜像成功（16,777,216 字节，Device Service `flash.verified=true`）；
  `esp32c5` / `esp32h2` build-only 成功；`--warnings all` 无新告警；PR CI 39/39 SUCCESS。
- 源码位置（head）：`common.inl:1082-1093` 保存，`:1108-1113` 恢复；
  C6 `spi_ll_master_init()` 写 PLL 在 IDF 5.5.5 `components/hal/esp32c6/include/hal/spi_ll.h:188`。

## 文件

- `report.md`：完整报告（因果链、IDF 调用链、代码核对、验证与边界）
- `run.json`：结构化记录
- `evidence/pr452.diff`：PR 完整差异
- `evidence/pr-metadata.json`：PR 元数据与 CI 结果
- `evidence/device-profile-summary.json`：脱敏后的设备 profile 字段
- `evidence/session-summary.json`：四个会话的 session id、固件/运行时哈希、画面哈希
- `evidence/build-summary.txt`：构建命令、产物大小与 SHA256、C5/H2 编译覆盖
- `evidence/register-derivation.md`：SCLK 换算公式与逐阶段寄存器值
- `evidence/serial-base-spi.txt`、`serial-head-spi.txt`：寄存器路径两版完整串口
- `evidence/serial-base-display.txt`、`serial-head-display.txt`：显示路径两版完整串口
- `evidence/frame-base-display.png`、`frame-head-display.png`：135×240 画面（同一 SHA256）
- `evidence/sketches/`：两份复现 sketch 与会话采集脚本

## 已发布回复

- <https://github.com/m5stack/M5GFX/pull/452#issuecomment-7235935941>
  （1 条，英文；PR 仍 OPEN，未 close、未 push、未改他人仓库）
- 公开记录 permalink（评论引用）：`523cac9`

## 未覆盖项

- `hardware validation`：`NOT RUN`；SCLK 波形未测量，`esp32sim` 不建模 SPI 频率，
  记录中的频率由 mux/分周寄存器换算。
- C5 / C61 / H2 运行时 `NOT RUN`；C61 仅有 PR CI 构建结果，本机 3.3.13 无 C61 目标。
- Arduino 4.0 / IDF 6.x 未在本机运行，仅做源码核对并引用 PR CI。
- `readRect` 读回未复验：虚拟 ST7789 只实现 RDDID，不实现 RAMRD。
- 未测试 `use_lock=false`、>40 MHz 写、长稳/热复位或与其他 IDF SPI 使用者混用。
