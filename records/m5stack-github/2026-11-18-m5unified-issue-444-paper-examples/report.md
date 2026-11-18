# m5stack/M5Unified #444 报告

## 1. 条目与诉求

- Issue：https://github.com/m5stack/M5Unified/issues/444
- 标题：M5Paper examples still route to M5EPD
- 作者：stevejoung（非机器人）
- 状态：OPEN，2026-11-18T11:11:07Z 创建，无评论
- 正文全文：`Please add an M5Paper example on the M5Unified stack, the Paper docs still route to M5EPD`

诉求可以拆成两点：

1. 在 M5Unified 上补一个 M5Paper 示例；
2. 指出 Paper 文档仍然把人引向 M5EPD。

本条不是重复项，也没有被处理过，需要一条回复。

## 2. 方法

按证据优先级尝试运行时路径，再退回代码级：

1. 查本机 Device Service 的设备目录（`GET /api/v1/devices`，36 个 profile），确认是否存在
   M5Paper（ESP32-D0WDQ6-V3 + IT8951 e-paper）profile；
2. 查 esp-emulator 的 `devices/esp32-lx6` 机型目录；
3. 取 M5Unified 0.3.0（`96576a1`）与 M5GFX（`28d4794`）源码，核对板型支持、面板构造、
   EPD 刷新与示例覆盖；
4. 抓取 `docs.m5stack.com/en/core/Paper` 与 `/en/arduino/m5paper/program` 线上内容；
5. 尝试安装 `esp32:esp32` 核心做最小 sketch 的编译检查（失败，见 §5）；
6. 按条目语言（英文）准备一条回复。

## 3. 发现（代码级）

### 3.1 M5Unified 已支持 M5Paper

- `README.md:60` 在 "Supported devices (ESP32)" 下列出 `M5Paper`。
- `src/M5Unified.inl:153` 给出 I2C/PortA 引脚（GPIO22/21、32/25）；`:1839` 为按键设置输入
  模式；`:2988` 从 GPIO37/38/39 读取 BtnA/B/C（`raw_gpio32_39 >> 37 & 0x07`）。
- 0.3.0 声明 `depends=M5GFX (>=0.3.0)`。

### 3.2 显示与触摸由 M5GFX 提供

- `src/board_detect/m5/esp32_d0wdq6_construct.inl:192-203` 的 `construct_paper()` 构造
  `Panel_IT8951`，并挂 `Touch_GT911`。
- `src/M5GFX.cpp:1105-1113` 对 `board_M5Paper` 设 `540x960`、`grayscale_8bit`、rotation 0。
- `src/lgfx/v1/panel/Panel_IT8951.inl:116` `_auto_display = true`；`src/lgfx/v1/Panel.hpp:88`
  在 `endWrite()` 归零时调用 `display(0,0,0,0)`，即一次写事务结束会把脏区刷到面板。
- `setEpdMode()` 在 `src/lgfx/v1/LGFXBase.hpp:1440`，4 档：`epd_quality`（GC16，默认）、
  `epd_text`（GL16）、`epd_fast`（DU）、`epd_fastest`（DU4），见 `Panel_IT8951.inl:487-494`。

### 3.3 缺的是示例，不是驱动

- 0.3.0 的 `examples/` 共 58 条路径、18 个 `.ino`，没有任何 Paper 专用 sketch
  （`evidence/examples-tree.txt`）。
- 现有示例是跨板的：`examples/Basic/HowToUse/HowToUse.ino:338` 只是把 `board_M5Paper`
  映射为名字 `"Paper"`，其余绘制/按键逻辑对所有板一致。
- `.github/workflows/ArduinoBuild.yml` 的 M5Stack Board Manager 段只构建
  `m5stack:esp32:m5stack_core` 与 `m5stack:esp32:m5stack_cores3`，没有 `m5stack_paper`；
  即使新增 Paper 示例，CI 也不会编译它。

### 3.4 文档确实仍把 Paper 引向 M5EPD

线上 `https://docs.m5stack.com/en/core/Paper`（2026-11-18 抓取）的 Softwares → Arduino
仍渲染：

- `Paper v1.1 Arduino M5EPD Driver Library`
- `Paper v1.1 Arduino M5EPD_Todo`
- `Paper v1.1 Arduino M5EPD_Calculator`
- `Paper v1.1 Arduino M5EPD_TTFExample`
- `Paper v1.1 Arduino image2gray tool`（指向 M5EPD 的 tools）

而 `https://docs.m5stack.com/en/arduino/m5paper/program` 已经安装 `M5Unified >= 0.2.5`、
`M5GFX >= 0.2.7`，并在 "Deprecated Examples" 里写明 M5EPD 库不再维护、推荐改用
M5Unified/M5GFX，示例指向 M5GFX 的 `BarGraph`。

`m5stack/M5EPD` 已归档（`archived: true`），其 README 首行是
"🚫 Deprecated — Use M5GFX & M5Unified"。

结论：作者看到的是产品页的资源链接列表；快速上手页其实已经迁移。

## 4. 拟发布回复（英文，一条）

````markdown
Thanks — the docs complaint is correct, and it is worth separating the two halves of this.

**1. M5Unified already supports M5Paper.** It is in the supported-device list (`README.md:60`
at `96576a1`, 0.3.0), and the board is wired up in the pin/button tables
(`src/M5Unified.inl:153`, `:1839`, `:2988`; BtnA/B/C on GPIO37/38/39). The display and touch
come from M5GFX: `construct_paper()` builds a `Panel_IT8951` plus `Touch_GT911`
(`src/board_detect/m5/esp32_d0wdq6_construct.inl:192-203`), configured as 540x960
`grayscale_8bit` (`src/M5GFX.cpp:1105-1113`). E-paper refresh modes are exposed through
`M5.Display.setEpdMode()` (`epd_quality` / `epd_text` / `epd_fast` / `epd_fastest`,
`src/lgfx/v1/LGFXBase.hpp:1440`), and `Panel_IT8951` sets `_auto_display = true`, so ending a
write transaction (`endWrite()`) pushes the dirty region to the panel.

**2. What is missing is an example, and the stale docs links.** At `96576a1` there are 18
sketches under `examples/` and none is Paper-specific — they are board-agnostic, and
`Basic/HowToUse` only maps `board_M5Paper` to the name "Paper" (`HowToUse.ino:338`). On the
docs side, https://docs.m5stack.com/en/core/Paper still lists "Paper v1.1 Arduino M5EPD
Driver Library" plus M5EPD_Todo / M5EPD_Calculator / M5EPD_TTFExample; that repository is
archived and its README starts with "Deprecated — Use M5GFX & M5Unified". The Paper Arduino
quick start page already installs M5Unified and marks the M5EPD examples as no longer
maintained, so the product page link list is the part that still routes people to M5EPD.

Evidence class: **code-level verification**. `NOT RUN`: hardware and virtual-device validation.
Why no virtual-device validation: the local device catalogue has no M5Paper profile
(ESP32-D0WDQ6-V3 + IT8951); its e-paper profiles (PaperMono / PaperColor / PaperS3 / PaperDIY)
are all ESP32-S3 boards with different panels and do not exercise the IT8951 path. No compile
check either: this host has no Arduino-ESP32 toolchain, and installing it here did not complete
(disk space).

A minimal M5Unified Paper sketch is roughly this (APIs checked against the sources above, not
compiled here):

```cpp
#include <M5Unified.h>

void setup() {
  M5.begin(M5.config());

  M5.Display.setEpdMode(m5gfx::epd_mode_t::epd_quality); // epd_text / epd_fast / epd_fastest
  M5.Display.startWrite();          // one refresh for the whole first screen
  M5.Display.fillScreen(TFT_WHITE);
  M5.Display.setTextColor(TFT_BLACK, TFT_WHITE);
  M5.Display.setTextSize(3);
  M5.Display.setCursor(24, 60);
  M5.Display.println("M5Paper");
  M5.Display.endWrite();            // auto_display pushes the region to the panel
}

void loop() {
  M5.update();
  if (M5.BtnA.wasClicked()) {
    M5.Display.startWrite();
    M5.Display.fillRect(0, 240, M5.Display.width(), 48, TFT_WHITE);
    M5.Display.setCursor(24, 244);
    M5.Display.printf("BtnA clicks: %u", (unsigned)M5.BtnA.getClickCount());
    M5.Display.endWrite();
  }
  delay(10);
}
```

If a Paper example is wanted, `examples/Basic/` is the natural home (an e-paper demo covering
`setEpdMode()` and partial updates). Note that the ArduinoBuild CI matrix only builds
`m5stack_core` and `m5stack_cores3` among the M5Stack boards, so a new Paper sketch would not
be compiled unless `m5stack:esp32:m5stack_paper` is added to the matrix.

Detail: <public work-log permalink>
````

## 5. 构建尝试（失败，未产生结论）

本机无 Arduino-ESP32 工具链。尝试：

```bash
arduino-cli 1.6.0 core install esp32:esp32   # 3.3.12
```

下载约 1.7 GiB 后在安装 `esp32:esp-x32@2601`（xtensa-esp-elf）解压阶段失败：
`Create file .../xtensa-esp-elf/lib/esp32s2/libstdc++.a: no space left on device`
（当时卷可用约 0.9 GiB，已解压的 `esp-rv32` 占 2.0 GiB）。临时目录已清理，未留下编译产物，
因此没有任何「编译通过/失败」的结论，回复中也不声称编译过。

## 6. 未覆盖项

- 未编译 `code/PaperHello`；代码只按源码签名核对过（`config()`、`setEpdMode()`、
  `startWrite/endWrite`、`fillScreen/fillRect/printf`、`BtnA.wasClicked/getClickCount`、
  `Power.getBatteryVoltage()`）。
- 未在 M5Paper 实机烧录，因此 EPD 刷新时间、GC16/DU 实际观感、GT911 触摸、AXP192 电源行为均未观测。
- 没有虚拟设备验证：本机没有 M5Paper profile，最近的 e-paper profile 是 ESP32-S3 + 其它面板。
- 未评估维护者是否接受 Paper 专用示例，也未评估文档侧改动的归属仓库（产品页链接列表）。
