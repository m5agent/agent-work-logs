# Tab5 原版 ST7123 取帧和 GT911 拖动

日期 2026-11-17。Virtual-device validation。用同一个隔离 Device Service，
按上传镜像规范化后的 SHA-256 选择板型。两个原版均以 esp-emu 1.1.0
macOS arm64 运行，SHA-256
633a35f993300a765634ed78a2dbcfd5ffcd5c3f2f354a2dddabeb6108240828。
两个会话均未提供匹配 ELF。本记录的独立运行执行源码为 4fc493abdb305afb795a91f8d2639e71cca5c25f。Tab5 选入集成的提交为 fd823aeb37f5c89c93000df042cd6692a2771a3b，组合候选为 693c56948c2458cf8e24c800832f7600438f4b45。此处的执行数据来自独立运行。

## 原版 Arduventure 1.0.0

原始 BIN SHA-256
e2f228813b719b81c47a8deaa7576f1b83e61e950c6178c5cf570bfaca7b8616，
规范化并实际执行的 Flash SHA-256
0922e46d70edc11d285fd3d4023a18f061d4d95fd8e7a1729e00702cc3dba063。

| 对照配置 | 同一原版结果 |
| --- | --- |
| 仅原生 DSI | 串口报 Wrong display geometry。DSI 已连接，142 次帧请求返回 409。 |
| 硬件 I²C1 的 ST7123 静态版本寄存器 | 相同串口 SHA 和几何错误。142 次帧请求仍返回 409。 |
| 硬件 I²C1 的 GT911 静态身份寄存器 | 相同串口 SHA 和几何错误。141 次帧请求仍返回 409。 |
| 原生 ST7123 GPIO I²C Part | 串口选择 ST7123、初始化 PPA 和 DSI DMA。原始 720×1280 帧同时显示操作区和 ARDUBOY TEAM A.R.G. PRESENT 启动画面。 |

三个失败对照的串口 SHA-256 均为
1d1fac9d762790812fae6843eaa8935d55c49a7d7c5b9c376f4c83631a479add。
独立的只读 GPIO 观察器从 SDA31/SCL32 解出五次对 PI4IO 0x43 的写地址，
其 9 位周期的 ACK 位保持释放。该对照没有能在 GPIO 总线上驱动 SDA 的
外部设备，硬件 I²C 寄存器设备不能回答这一路。原版包含 M5GFX 软件总线
探测日志串。修复后的 Part 直接观察主机 SDA/SCL 边沿，在 ACK 和读周期
驱动从端 SDA；寄存器组覆盖必要的 0x43、0x44 和 0x55 探测。原版串口明确
输出 ST touch FW version 03 与 detected ST7123 display。 [M5GFX 检测源码](https://github.com/m5stack/M5GFX/blob/28d47949bdc84f30881623476f555398e2194313/src/board_detect/m5/esp32p4.inl)

同 worker 正控的 ST7123 Part SHA-256
6eaa3664fd81ce7e8f56bc0f84ad124ca2afcce21c947e74bbb41f1d9802d106，
有游戏像素的原始 PNG SHA-256
b132be51149e62583817538364084b4f31f31f16b54e9f8c89313dd861bc4348，
串口 SHA-256
988e37642531b0f68e50fa90808c9f27d34ca49304c288402222b8b1c8655b0d，
会话 ZIP SHA-256
6fe123d380915f39883f457ce69e8ba70d42dda2e4a8260b44273e308d868601。
普通输入端点仍对 ST7123 会话返回 input_requires_matching_elf。

## GT911 数据面与 CarPlay 对照

在正常 POST /input 路径，ESP-IDF 控制器探针
0e7a9596ffe0c2725ad34c69be6cf16a80963580208d0640be18886dd521aeaf
从 GPIO23 低有效 IRQ 和 HP I²C1 读取严格有序的唯一位置：
(120,200)、(220,360)、(320,520)、(420,680)、(520,840)、(620,1000)。
最后一个报告是释放，全部 22 份报告均经 0x814e 确认。探针 ZIP SHA-256
6410a26e8a927d304a152f73c51a36f3c191bdc274f8b426efbcf3ac402db3e1。
探针使用 ESP-IDF v5.5.4、P4 revision < 3 和 16 MiB Flash。

同一隔离 worker 保持默认 gt911-ili9881c，选择 CarPlay 原始 BIN
4f3bb118a5570a6ba885a234fce55b66e28ef26091cfe4f3f2e4c33711471ea3
及执行 Flash ff578ccc3f4f93a6f431eff0809b1e46bfb3951101c81bc676774d3f3a36387b。
既有 GT911 Part SHA-256
a0852d08d6cc04a11dcdd57c417b497f857be3e6265f8b690968ae3338cd3ce9。
空白区拖动 (320,500)→(500,900) 的 24 份报告均经来宾确认，图像 SHA
保持不变。随后点 (640,160) 打开 Clear phone pairing?；确认框原始 PNG
SHA-256 bf357f04e40dc9cb76f7e34df7b94a45a89f97da7df26f813fac35577103eed3。
没有确认清除。该会话 ZIP SHA-256
0e5c5865eceb4bf1080bef62630598693a36fdd00038a73cbd8fbbdce7bcd26d。

## 集成源码隔离复审

原版 Flash 和运行时身份仍见上面各段。使用模拟器源码 `693c56948c2458cf8e24c800832f7600438f4b45` 与审核器 `393322693d4a5ba3341ae925e726cf68b80cc395` 进行隔离 dry-run。两个原版都取得 720×1280 DSI 截图，且 60 秒观察通过。

| 原版 | 观察时长 | 普通审核输入 | 审核结果 |
| --- | ---: | --- | --- |
| Arduventure 1.0.0 | 60.255 s | 点击返回 `input_requires_matching_elf`，拖动返回 `unsupported_input` | `manual_review` · `SIM_PARTIAL` · `E_INTERACTION_INPUT_UNSUPPORTED` |
| CarPlay 1.0.0 | 60.239 s | 中央点击和拖动均被接收，采样窗口内画面未变 | `manual_review` · `SIM_PARTIAL` · `E_INTERACTION_CLAIM_PARTIAL` |

这一轮 Arduventure 的截图通过审核就绪条件，独立原生会话的彩色游戏画面负责应用画面验证。CarPlay 的普通审核动作与前述指定按钮点击分别有独立的输入和画面证据。没有 Burner 提交。[精确摘要](evidence/review-dry-run-summary.json)

最终候选 `37fc8963d77bf806cde4fa16ea11e31b5a98b4d7` 只调整传感器测试 ZIP 时间戳。以该精确源码独立复审，Arduventure 观察 60.272 秒，CarPlay 观察 60.256 秒，截图、输入观察和两条人工复核原因再次一致。没有 Burner 提交。[最终源码隔离复审](evidence/release-source-review-summary.json)

## 复现与范围

用 Rust 1.88.0、wasm32-unknown-unknown 和锁定的 esp-emu v1.1.0 ESP Part SDK 构建部件，比较上文两个 SHA-256。

```sh
rustup target add --toolchain 1.88.0 wasm32-unknown-unknown
RUSTUP_TOOLCHAIN=1.88.0 python3 platform/esp-parts/tab5-st7123-gpio/build.py \
  --output "$PWD/.work/tab5-st7123-gpio-board"
RUSTUP_TOOLCHAIN=1.88.0 python3 platform/esp-parts/tab5-gt911/build.py \
  --output "$PWD/.work/tab5-gt911-board"
```

在隔离 worker 配置匹配 SHA 的 M5_TAB5_DSI_EMULATOR、M5_TAB5_GT911_PART 和 M5_TAB5_ST7123_I2C_PART，保留默认 M5_TAB5_DSI_BOARD=gt911-ili9881c。将上述两个执行 Flash SHA 一起加入 M5_TAB5_DSI_FIRMWARE_SHA256S，仅将 Arduventure 映射到 ST7123。

```sh
export M5_TAB5_DSI_BOARD_OVERRIDES='{"0922e46d70edc11d285fd3d4023a18f061d4d95fd8e7a1729e00702cc3dba063":"st7123"}'
```

用两个合法获得的原版先后建立 Tab5 原生会话。每个会话通过
`GET /api/v1/sessions/{id}/frame.png?max_age_ms=0&orient=panel` 检查原始
面板帧和串口，通过 `POST /api/v1/sessions/{id}/input` 执行上述触控对照。
控制器探针构建命令和发送方式见同一源码的 `tests/firmware/tab5_gt911/README.md`。
结束前下载并校验会话 ZIP。停止后释放 Flash 和所有租约。Burner 提交保持禁止。

上游运行时与既有 GT911 部件身份保持一致。ST7123 仅匹配显式允许的 Flash SHA，
未匹配的上传固件保留此前的回退行为。回滚时恢复原有 Device Service 和部件配置，
移除该 SHA 的板型覆盖与 GPIO I²C Part 设置。

Arduventure 通过板型探测与实际启动画面。ST7123 触控、多点与游戏操作
仍未验证。CarPlay 的拖动覆盖控制器和空白区域行为，原应用没有该拖动
的功能响应。USB/iPhone 数据面、浏览器触点映射、实际板卡和物理总线电气
参数仍未验证。

[原生会话证据摘要](evidence/tab5-native-summary.json)
