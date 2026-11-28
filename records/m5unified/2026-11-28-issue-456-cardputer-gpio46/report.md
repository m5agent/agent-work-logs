# M5Unified #456 Cardputer ADV GPIO46 保持输出 报告

## 背景

- 来源：https://github.com/m5stack/M5Unified/issues/456（作者 Reytian）
- 现象：Cardputer ADV 上 `M5.begin()` 后 GPIO46 仍为输出并驱动高。GPIO46 同时是 ES8311 的
  ASDOUT（麦克风数据），结果 `M5.Mic.record()` 只能读到常量（原始 I2S 字 `0xFFFF`，
  默认增益下 `0xFFF8`）。
- 目标：确认根因是否成立、影响哪些板卡、并验证最小修复能否在运行时消除输出使能。

## 结论

- 状态：根因确认；最小修复在虚拟设备寄存器层通过。完整音频现象未在模拟器复现，记录为 `PARTIAL`。
- 根因：`M5.begin()` 在板卡未知时把 GPIO46 当作 Capsule/Dial/DinMeter 的电源保持脚驱动高；
  板卡识别后，`M5Unified.hpp` 的恢复 `switch` 只包含 CoreS3 / CoreS3SE / StackChan /
  AtomS3R Cam / AtomS3R Ext / StampS3 / StampS3Bat。Cardputer、Cardputer ADV 和 PaperMono
  虽然把 GPIO46 用作麦克风数据脚，却不在列表中。
- 为什么 `M5.Mic.begin()` 没修好：`Mic_Class::_setup_i2s()` 只调用
  `i2s_channel_init_std_mode()` / `i2s_channel_init_pdm_rx_mode()`；ESP-IDF 的
  `i2s_gpio_check_and_set()` 对输入脚只做 `gpio_func_sel()`、`gpio_input_enable()` 和
  输入信号连接，不关闭输出使能。此前 PR #345 的描述假定“Cardputer / PaperMono 的麦克风
  数据脚会被 M5Unified 自己重新配置”，该假定不成立。
- 改动范围：`src/M5Unified.hpp` 的恢复分支新增三块板；不改公共 API，不影响以 GPIO46 为
  显示总线或电源保持的板卡。

## 证据

### 代码或配置

固定版本：`m5stack/M5Unified @ 96576a14247ddc935149145aa6b51943464120f1`（0.3.0）。

电源保持与恢复：

```cpp
// src/M5Unified.hpp:357-362
m5gfx::gpio::pin_backup_t gpio46_backup(GPIO_NUM_46);
if (gpio46_hold)
{
  m5gfx::gpio_hi(GPIO_NUM_46);
  m5gfx::pinMode(GPIO_NUM_46, m5gfx::pin_mode_t::output);
}

// src/M5Unified.hpp:417-430（修复前的现状）
switch (gpio46_hold ? board : board_t::board_unknown)
{
case board_t::board_M5StackCoreS3:
case board_t::board_M5StackCoreS3SE:
case board_t::board_M5StackChan:
case board_t::board_M5AtomS3RCam:
case board_t::board_M5AtomS3RExt:
case board_t::board_M5StampS3:
case board_t::board_M5StampS3Bat:
  gpio46_backup.restore();
  break;
default:
  break;
}
```

麦克风数据脚（三块板都把 GPIO46 作为 `pin_data_in`）：

```cpp
// src/M5Unified.inl:2179-2186
case board_t::board_M5PaperMono:
  mic_cfg.pin_ws = GPIO_NUM_45;
  mic_cfg.pin_data_in = GPIO_NUM_46;

// src/M5Unified.inl:2222-2238
case board_t::board_M5Cardputer:
  mic_cfg.pin_data_in = GPIO_NUM_46;
  mic_cfg.pin_ws = GPIO_NUM_43;
case board_t::board_M5CardputerADV:
  mic_cfg.pin_data_in = GPIO_NUM_46;
  mic_cfg.pin_ws = GPIO_NUM_43;
  mic_cfg.pin_bck = GPIO_NUM_41;
```

ESP-IDF 输入脚配置（Arduino-ESP32 3.3.x 对应的实现，按 v5.5.4 复核）：

```c
// components/esp_driver_i2s/i2s_common.c, i2s_gpio_check_and_set()
if (is_input) {
    gpio_func_sel(gpio, PIN_FUNC_GPIO);
    gpio_input_enable(gpio);
    esp_rom_gpio_connect_in_signal(gpio, signal_idx, is_invert);
}
```

### 构建

- `arduino-cli 1.6.0`
- FQBN：`esp32:esp32:m5stack_cardputer`
- 依赖：M5Unified 0.3.0、M5GFX 0.3.0
- sketch：`code/m5u456/m5u456.ino`，SHA-256
  `a5d55fec62bbef981c54936c297782ea1d521d40a9082c31cbb93274744e6c22`
- 修复前 merged BIN SHA-256：
  `977d75545a4a91b1bf87faa00dada126b4cbf659a4144597785abe714d7caecc`
- 修复后 merged BIN SHA-256：
  `d3a251e0404ab2f5ab2bf71e30140240a9bbee0812c78ac27ba48164331f794d`

### 执行

在本机 Device Service 创建 `esp32sim` 会话，分别使用 `cardputer-adv`、`cardputer`、
`papermono` 设备 profile。串口读取 `GPIO_ENABLE1_REG`（`0x6000402C`）和
`GPIO_OUT1_REG`（`0x60004010`）的 bit14（GPIO46）。

修复前：

| 板卡 | board_t | after begin | after Mic.begin | after set input |
| --- | --- | --- | --- | --- |
| Cardputer ADV | 24 | `EN1=0000487e OUT1=00004026 en46=1 out46=1` | `EN1=00004a7e OUT1=00004026 en46=1 out46=1` | `EN1=00000a7e en46=0` |
| Cardputer | 14 | `EN1=0000487e OUT1=00004026 en46=1 out46=1` | `EN1=0000487e OUT1=00004026 en46=1 out46=1` | `EN1=0000087e en46=0` |
| PaperMono | 29 | `EN1=0001c800 OUT1=0001c000 en46=1 out46=1` | `EN1=0001e800 OUT1=0001c000 en46=1 out46=1` | `EN1=0001a800 en46=0` |

修复后：

| 板卡 | board_t | after begin | after Mic.begin |
| --- | --- | --- | --- |
| Cardputer ADV | 24 | `EN1=0000087e OUT1=00000026 en46=0 out46=0` | `EN1=00000a7e OUT1=00000026 en46=0 out46=0` |
| Cardputer | 14 | `EN1=0000087e OUT1=00000026 en46=0 out46=0` | `EN1=0000087e OUT1=00000026 en46=0 out46=0` |
| PaperMono | 29 | `EN1=00018800 OUT1=00018000 en46=0 out46=0` | `EN1=0001a800 OUT1=00018000 en46=0 out46=0` |

原始串口日志见 `evidence/*-serial-console.log`；采集时控制台使用 CRLF，保存时统一为 LF，未删改行内容。

### 修复

```diff
       switch (gpio46_hold ? board : board_t::board_unknown)
       {
+      case board_t::board_M5PaperMono:
+      case board_t::board_M5Cardputer:
+      case board_t::board_M5CardputerADV:
       case board_t::board_M5StackCoreS3:
       case board_t::board_M5StackCoreS3SE:
```

patch 见 `patches/0001-restore-gpio46-on-cardputer-papermono.patch`，基于
`96576a14247ddc935149145aa6b51943464120f1`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | arduino-cli 构建成功，merged BIN 已生成 |
| flash | PASS | 虚拟设备会话进入 running，ROM 串口日志完整 |
| transport | PASS | 三块板串口输出 `M5U456` 标记完整 |
| device_response | PASS | `GPIO_ENABLE1_REG`/`GPIO_OUT1_REG` bit14 修复前为 1、修复后为 0 |
| data_behavior | NOT RUN | 未注入音频 fixture，未复现常量 PCM 样本 |
| visual_or_physical | NOT RUN | 不涉及 |
| hardware | NOT RUN | 测试中心无 Cardputer ADV 实机 |

## 验证边界

模拟器 GPIO 模型在 `esp-periph/src/gpio.rs` 的 `resolve()` 中明确注明不模拟对驱冲突：
外部驱动的输入电平优先于被使能的输出。因此即使 GPIO46 仍为输出，注入的 ES8311 PCM 仍会
作为“理想数字源”进入 I2S RX，无法复现常量样本。本次验证覆盖的是根因寄存器状态和修复效果，
不是对真实电气对驱的替代。作者的 OpenOCD 读数与实机麦克风现象仍是该症状的硬件证据。

## 风险与回滚

- 修复只影响板卡识别后、`gpio46_hold` 为真且板卡为 Cardputer / Cardputer ADV / PaperMono 的路径。
- 以 GPIO46 作为显示总线或电源保持的板卡仍在 `default` 分支，行为不变。
- 回滚方式：撤销上述三个 `case` 即可。
- 未对上游仓库提交或推送；patch 仅存于本记录。
