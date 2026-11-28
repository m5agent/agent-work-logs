# M5GFX PR #452 报告：`spi::init()` 在 ESP-IDF 主驱动初始化后恢复 Arduino SPI 时钟源

## 1. 条目与结论

- PR：[m5stack/M5GFX#452](https://github.com/m5stack/M5GFX/pull/452)，作者 `ainyan03`，英文，OPEN。
- Head `e1666e9c175725b426a7aef9e4b17622f1d9813a`，base `603092aab60e32fadd1d73abd472068a35e189e8`
  （develop tip）；单文件 `src/lgfx/v1/platforms/esp32/common.inl`，+18/-0。
- 评审前 comments / reviews 均为 0；PR CI 39 项全部 SUCCESS。
- 结论：**未发现阻塞合并的问题**。PR 在报告路径（ESP32-C6 + Arduino，M5GFX 与 Arduino `SPI`
  共用 SPI2）上恢复了 Arduino 初始化时选择的 XTAL 源，Arduino 的事务分周重新与源频率一致；
  M5GFX 自身的显示写入仍为 40 MHz，显示内容不变。

## 2. 问题与假设

Issue #451 的因果链（上一轮已在虚拟 Nesso N1 上复现）：

1. Arduino-ESP32 3.3.12+ 在 `spiStartBus()` 中把 SPI2 时钟源固定到 XTAL
   （C6 为 40 MHz），`spiSourceFrequency()` 按 XTAL 计算分周。
2. M5GFX 的 Arduino 路径在 `spi::init()` 里先 `SPI.end(); SPI.begin()`，随后调用
   ESP-IDF 的 `spi_bus_initialize()` / `spi_bus_add_device()`。
3. IDF 5.5.5 在 `spi_bus_add_device()` 懒初始化 master driver 时，C6/C61 的
   `spi_ll_master_init()` 把 `PCR.spi2_clkm_sel` 写成 1（PLL_F80M，80 MHz）。
4. Arduino 的分周仍按 40 MHz 计算，实际 SCLK 变成请求值的 2 倍（C6）。

PR 的做法：在 Arduino 路径、`spi_bus_initialize()` 之前保存 `PCR_SPI2_CLKM_CONF_REG` 的
`CLKM_SEL`（C5/C61 还含 `CLKM_DIV_NUM`），在 `spi_bus_add_device()` 之后、且
`_spi_handle[spi_host] != nullptr`（Arduino 总线已启动）时写回。

## 3. IDF 侧核对

- IDF v5.5.5（Arduino-ESP32 3.3.13 所用）：
  - C6 `components/hal/esp32c6/include/hal/spi_ll.h:188`：`spi_ll_master_init()` 写
    `PCR.spi2_clkm_conf.spi2_clkm_sel = 1`；
  - C61 同样写 1；H2 写 0（XTAL）；C5 的 `spi_ll_master_init()` 不写 mux。
  - 调用链：`spi_bus_add_device()` → `spi_master_init_driver()` → `spi_hal_init()` →
    `spi_ll_master_init()`；`spi_bus_initialize()` 本身不写 mux。
- IDF v6.1 本地树：`spi_ll_master_init()` 已不写 mux；源选择在
  `esp_hal_gpspi/src/gpspi/spi_master.c` 的 `spi_setup_device()`（实际 IDF 事务）里写。
  M5GFX 在 Arduino 路径只用 `spi_device_acquire_bus()` / `spi_device_release_bus()`
  （`common.inl:1258-1259`），不调用 IDF 的 `spi_device_transmit()`，因此 6.x 上本 PR
  在 add_device 后写回的是同一个值，不改变行为。
- 因此 PR 描述中的“IDF 5.x 在 C6/C61 的第一次 add_device 改变 mux、C5/H2 与 IDF 6.x
  不变”与源码一致。实际需要恢复的目标是 C6/C61；其余目标为 no-op，写回值相同。

## 4. 代码位置与实现核对

PR head `e1666e9`：

- `src/lgfx/v1/platforms/esp32/common.inl:1082-1093`：保存 `saved_clkm`；
  `clkm_mask` 包含 `PCR_SPI2_CLKM_SEL_M`，存在 `PCR_SPI2_CLKM_DIV_NUM_M` 时并入。
- `src/lgfx/v1/platforms/esp32/common.inl:1108-1113`：在 add_device 后用
  `(当前值 & ~clkm_mask) | saved_clkm` 恢复，条件为 `spi_host == SPI2_HOST` 且
  `_spi_handle[spi_host] != nullptr`。
- 保存点在 `spi_bus_initialize()` 之前，恢复点在 `spi_bus_add_device()` 之后；
  5.5.5 的 mux 写入发生在后者内部，覆盖了唯一会改变源的调用。
- 读改写只碰 SEL（及存在的 DIV_NUM），保留 IDF 置位的 `PCR_SPI2_CLKM_EN`（bit 22）。
- 恢复条件用 `_spi_handle` 判定“Arduino 总线已启动”，而不是“M5GFX 是否初始化了 IDF 总线”；
  在纯 IDF 使用场景 `_spi_handle` 为空，不写回。`initQuad()` 不启动 Arduino `SPI` 对象，
  不属于本报告场景；当前 C6 板级数据没有 QSPI 板。

## 5. 验证

### 5.1 环境

- macOS arm64；`arduino-cli 1.6.0`；`esp32:esp32 3.3.13`（ESP-IDF 5.5.5）。
- 本机 Device Service 的 `nesso-n1` profile，`runtime=esp32sim`，board `arduino-nesso-n1`，
  ESP32-C6，ST7789 135×240 / SPI2，16 MB flash；runtime commit `9c0447e8…`，
  binary `f87e8de0…`，`flash.verified=true`。
- 两棵只读库树：base `603092a`、head `e1666e9`，同一 sketch 分别构建。

### 5.2 寄存器路径（`nesso_spi_repro`）

步骤：`SPI.begin(20,22,21)` 后做一次 8 MHz 事务（Arduino 单独基线）→ `lgfx::Bus_SPI::init()`
（SPI2，40 MHz 写 / 16 MHz 读，Nesso N1 引脚）→ 再用 Arduino `SPI` 做 8 MHz、2 MHz 事务。
每次读 PCR mux 与 SPI2 分周寄存器，按 `evidence/register-derivation.md` 换算。

| 阶段 | base `603092a` | head `e1666e9` |
| --- | --- | --- |
| Arduino 单独 8 MHz | sel=0，div 5 → 8 MHz | sel=0，div 5 → 8 MHz |
| M5GFX 总线初始化后 | sel=1（PLL_F80M），div 5 → 16 MHz | sel=0（XTAL），div 5 → 8 MHz |
| Arduino 8 MHz（M5GFX 后） | 16 MHz | 8 MHz |
| Arduino 2 MHz（M5GFX 后） | 4 MHz | 2 MHz |

head 的第二次运行结果相同（`head-spi-rerun` 会话），说明结果可重复。base 与上一轮
Issue #451 的观测一致（`after_m5gfx_bus_init` sel=1、Arduino 8 MHz 变 16 MHz）。

### 5.3 显示路径（`nesso_display_repro`）

用 Nesso N1 的板级参数构造 `LGFX_Device`（ST7789，SPI2，40 MHz 写 / 16 MHz 读，
offset 52/40），并通过 0x44 的 PI4IOE 打开 LCD_READY / BACKLIGHT（与 M5GFX 的
`nesson1_power_on` + Light 亮度路径一致），然后 `display.init()`、整屏填充与两个矩形。

- head：`display_init=1`，135×240；`after_display_init` sel=0，
  `clk_equ_sysclk=1` → 40 MHz；整屏写入后 sel 仍为 0。
- base：同一流程 sel=1，div 2 → 40 MHz；整屏写入后 sel 仍为 1。
- 两版画面 PNG 完全相同：
  `b9db9630a017ab699f880893ff9946441345460389532682b9013c8ad40ff258`
  （蓝底 + 红块 + 绿块），说明恢复 XTAL 后面板命令与像素写入正常。
- `readRect` 在两版都返回 `0xffff`（`match=0`）：`esp32sim` 的 Nesso N1 模型只实现
  RDDID（0x04）读，未实现 RAMRD（0x2E）读回，因此无法在本虚拟设备上复验 PR 描述里的
  readback 一致性；这是模型边界，不是本 PR 的证据。

### 5.4 构建

- Nesso N1：四个镜像均构建成功（见 `evidence/build-summary.txt`），Device Service 均
  校验 `flash.verified=true`。
- `esp32c5`、`esp32h2`（3.3.13）build-only 成功；head 以 `--warnings all` 编译无新告警。
- PR CI 39/39 SUCCESS，含 C61（IDF 5.5.2）与 Arduino 4.0.0 / IDF 6.0.2 目标。

## 6. 影响面与评审意见

- 对 C6/C61 + Arduino 3.3.12+：修复了“M5GFX 初始化后 Arduino SPI 2×/4×”的问题；
  M5GFX 自身写时钟 40 MHz 不变（XTAL 40/1），读时钟 16 MHz 变为 40/3 ≈ 13.3 MHz
  （PR 正文已说明），属于性能取舍而非正确性问题。
- 对 C5/H2：IDF 5.5.5 不改变 mux（H2 写 0），写回同值，无行为变化；PR 的宏范围比实际
  需要宽，但无害。
- 对 IDF 6.x：add_device 不再改 mux，写回同值；M5GFX 不使用 IDF 事务，因此不改变行为。
- 对 C2：PR 明确未修；C2 不使用 `PCR_SPI2_CLKM_CONF_REG`，本补丁不覆盖，与描述一致。
- `use_lock=false` 时 M5GFX 不做每事务的源切换，写时钟 >40 MHz 会被限制在 40 MHz；
  PR 正文已列出，未发现额外回归。

非阻塞观察（无需在合并前处理）：显示读时钟从 16 MHz 变为 13.3 MHz，若后续有对
Nesso N1 `readRect` 性能敏感的使用，可单独评估。

## 7. 未覆盖项

- `hardware validation`：`NOT RUN`。本机无 C6 实机；真实 SCLK 波形未测量。
- `esp32sim` 不建模 GP-SPI 频率，表中的 SCLK 全部由 mux/分周寄存器换算。
- C5 / C61 / H2 运行时 `NOT RUN`；C61 仅由 PR CI 构建覆盖，本机 3.3.13 无 C61 目标。
- Arduino 4.0 / IDF 6.x 仅做源码核对与 CI 结果引用，本机未安装 4.0 运行。
- `readRect` 读回未复验（虚拟 ST7789 只实现 RDDID）。
- 未测试 `use_lock=false` 与 >40 MHz 写的运行时表现；未测试长稳、热复位或与其他
  IDF SPI 使用者的混用。

## 8. 已发布回复

- <https://github.com/m5stack/M5GFX/pull/452#issuecomment-7235935941>
  （1 条，英文；PR 仍 OPEN，未 close、未 push、未改他人仓库）
- 公开记录 permalink（评论引用）：`523cac9`；本条补充说明为同一记录的后续提交，不改变结论。
