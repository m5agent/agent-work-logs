# StickS3 控制器功能验证报告

本轮围绕 [#201](https://github.com/m5agent/m5stack-esp-emulator/issues/201)、[#202](https://github.com/m5agent/m5stack-esp-emulator/issues/202)、[#203](https://github.com/m5agent/m5stack-esp-emulator/issues/203) 和 [#204](https://github.com/m5agent/m5stack-esp-emulator/issues/204) 补齐 StickS3 固件审查的数据面。原始矩阵能看到应用画面，但 PM1 更新停在 IAP 入口，Bit Pirate 的 TinyUSB 初始化失败，AirMouseS3 没有对应的原生 BLE 路由，M5Gotchi 的启动扫描未发现 AP。此次保留固件自己的总线、端点和网络栈调用作为验证入口。

基线为 `67a2bf6b7511e3344eae2b04cf904fd70d64a79c`。最终源码为 `560005a20dc3e29d826561856ab58e21b10f2d79`，PR 为 `见后续交付记录`。最终集成运行时 SHA-256 为 `da00ee628a238429d0e1c84057bf1974350daacdc26fa03c6b7f38378c545611`。集成执行结果为 `122 层原生运行时通过官方 PM1 升级、坏 CRC 拒绝、ROM strap、Bit Pirate CDC 和 USB 复位控制。平台 2061 项，10 项跳过，无失败。`。下述独立运行仍绑定各自实际执行的二进制和输入镜像。 [证据摘要](evidence/validation-summary.json)

## PM1 固件更新与下载模式

原版 StickS3 PMIC Upgrade M5PM1-O 的 SHA-256 为 `35e5acdb0f6e503e0ddb65fc81b91d44ef0e10550aca87a945e9d3f0300582a4`。I2C 模型接收真实 IAP 入口、写入包和 RUN 命令。按 A 后，控制器收到 20,480 字节，`iap-upgrades=1`，回到应用地址 `0x6e`。其存储的 PM1 payload SHA-256 `e3c8e94171384af2b8f946e430617b71848efc385d63041206b1a5f3f9024ec7` 与固件内嵌 payload 一致。

坏 CRC 对照只改内嵌 PM1 镜像并修复外层 ESP32 镜像校验。固件仍传输 20,480 字节，模型拒绝 12 次 RUN，升级计数保持 0，停留在 bootloader 地址 `0x54`。另一轮观察 PWR 长按时的下载请求，松开后看到 `DOWNLOAD(USB/UART0)` 和 `waiting for download`，随后短按回到 `SPI_FLASH_BOOT`。这三条模型验证使用 `243073b1200d19395c285aaade91f9050ee4f870d58e4fa753cc483be78302c4`。

独立 HWCDC 轮次在运行时 `28215f00598f73659c992872725003a624400f76e03ac5e0918a6ee66e827b66` 上复核同一原版固件。USB Serial/JTAG 证据成员包含应用自身的 `=== Firmware upgrade completed ===`。该成员收集 381 个包、8,260 字节，与 UART0 分开，归档 ZIP 中的成员 SHA-256 一致。这轮验证补齐固件完成标记，前述模型轮次仍保持独立身份。 [PM1 与 HWCDC 证据](evidence/validation-summary.json)

较早的 IAP 候选运行中，QEMU 主机进程以 `-11` 退出。另一条下载模式候选曾进入 ROM，并返回 SPI Flash 启动，随后 guest 在 `spinlock_acquire` 断言后再次复位。两条均保留为 `FAIL`。后续正常通过限定用例，不能用于推断长期复位稳定性。

## USB OTG 与原版 Bit Pirate

在运行时 `243073b1200d19395c285aaade91f9050ee4f870d58e4fa753cc483be78302c4` 上，原版 Bit Pirate v1.6（SHA-256 `a93557398b87a50ac1bbd99ff98e93fb842bff0f0f3634d463d4d53497f8747e`）通过虚拟 USB host 对 ESP32-S3 OTG device FIFO 完成枚举，读取 device、configuration 和 HID report descriptor，设置地址和配置。CDC line coding 依次验证 115200、57600、115200。

通过 StickS3 B 和 A 选择 USB Serial，主机在 EP3 发 CRLF 并收到 ACK，从 EP4 收到 406 字节，其中包含 guest 的 `Press any key to start` 和 `HIZ>`。这是原版应用的 CDC 功能证据。HID report descriptor 读取只覆盖描述符请求。USB Serial/JTAG 是上一节独立的传输，不能与 OTG CDC 合并为一个控制器结论。 [Bit Pirate 发布件](https://github.com/geo-tp/ESP32-Bit-Pirate/releases/tag/v1.6) · [USB 证据](evidence/validation-summary.json)

## BLE HID 主机与原版 AirMouseS3

现有 Bumble H4 对端增加 HID 主机模式。它发现 `0x1812`，读取 Report Map 和 `0x2908` Report Reference，按需发起 SMP，然后订阅 Input Report 的 CCCD。主机按 Report Map 校验 payload 长度。StickS3 H4 夹具通过加密的 Report Map 读取触发配对，主机只在内存保留 bond。QMP 注入 A 按下、松开，guest 的 BtnA API 经 NimBLE 发出 Report ID 1 的两个 4 字节值 `01000000`、`00000000`，两者都由主机在 `0x2A4D` 实际收到。现有 NUS 在独立运行中仍得到 `BLE_BUMBLE_PASS cycles=1`。

原版 AirMouseS3 v1.0（SHA-256 `bdb567de990ef5c2a0fd113c033b259acd17e49717c9fdb5e9cc9d3776b208d8`）在同一 118 层 QEMU 上保留 `Waiting for pair` 画面。30 秒观测期间，已启动的 UART1 H4 对端没有收到 guest HCI 包。原版使用内置 ESP32-S3 NimBLE 控制器，当前 StickS3 QEMU 没有连接该控制器的 HCI 路由。官方 esp-emu v0.51.0 原生路径在执行前要求 `--elf`。应用描述符指定 ELF SHA-256 `a0227b121aae8dbc311f652875a60bb1294fd0b1f444f0b0c03c3c1a7322dbab`，原版公开发布只提供 BIN。原版的配对和报告仍未执行。 [AirMouseS3 发布件](https://github.com/Teapot174/AirMouseS3/releases/tag/v1.0) · [Espressif BLE 路由](https://github.com/espressif/esp-emulator/blob/main/docs/guides/BLE.md) · [HID 证据](evidence/validation-summary.json)

## Wi-Fi monitor 与受控 TX

独立 Device Service 会话在 guest 启动前核对只有一个虚拟 ESP32-S3 Wi-Fi NIC、无宿主网络后端。使用固定 channel 1 beacon 对照。IDF v5.5.4 SDK 探针在启用 promiscuous 模式前收不到匹配回调，启用后解析 81 字节 MPDU。控制器轨迹记录 129 字节 RX DMA 和 guest IRQ clear。无线电关闭的对照没有匹配 beacon 或 RX DMA。

同一 SDK 探针通过 `esp_wifi_80211_tx` 提交 43 字节的无害 Probe Request。控制器记录 47 字节帧、TX DMA outlink 和 TX IRQ 的 guest clear，虚拟 AP 返回 75 字节 Probe Response。当前证据是 TX 长度、描述符、IRQ 和虚拟响应，不含任意 TX payload 的逐字节捕获。

原版 M5Gotchi v0.7（SHA-256 `50425b34eb8b4f2b3dea7c85753e37f649c995bfae72b6189e4454077d686246`）在同一运行时上完成 Arduino 启动扫描。带夹具时两次扫描分别找到 1 个 AP，关闭虚拟无线电时均为 0。原版 Evil-StickS3 的扫描补验另列，混杂模式待验收。

原版 Evil 扫描补验使用 121 层原生运行时。经原版菜单执行 Scan WiFi 和 Select Network，启用夹具时列表显示合成 AP 与信道、RSSI，关闭虚拟无线电时列表为空。首轮串口观察缺应用标记，保留为 `PARTIAL`。两次正式会话均先核对无宿主网络后端，并在取证后停止。 [Evil 原版扫描补验](evidence/evil-stock-summary.json)

## 122 层组合复验

原版 PM1 按 A 写入并校验 20,480 字节，CDC 捕获 8,196 字节并含完成标记。坏 CRC 负控仍留在 bootloader，PWR 长短按进入 ROM 并回到应用。较早复跑另有一次写满后未见完成日志。原版 Bit Pirate 在同一二进制再次返回 406 字节 CDC 输出。复位负控证实旧模型提前接收的 SETUP 被 guest RX flush 清掉，新模型在中断确认前回 NAK，重试后 FIFO 数据一致。 [PM1](evidence/pm1-release-summary.json) · [USB](evidence/usb-release-summary.json)

## 复现

使用精确匹配的 QEMU 和 ROM 启动自有 Device Service，使用独立状态目录和专用访问凭据。各测试运行中先留存证据，再停止会话并保留历史。只在忽略目录或外部输出目录保存原始产物。

```sh
python3 tests/firmware/sticks3_pm1/run.py \
  --service "$OWNED_SERVICE_API" --firmware "$PM1_IMAGE" \
  --runtime-binary "$QEMU_XTENSA" --output-dir "$OUT/pm1-iap" --mode iap

python3 tests/firmware/sticks3_usb_otg/run_test.py \
  --api "$OWNED_SERVICE_API" --session "$OWNED_SESSION" \
  --token-file "$OWNED_TOKEN_FILE"

python3 platform/tools/ble_probe.py --protocol hid \
  --port "$OWNED_HCI_PORT" --name-prefix STICKS3-HID-FIXTURE \
  --hid-pairing auto --hid-min-reports 2

python3 tests/firmware/sticks3_wifi_monitor/run_test.py \
  --service "$OWNED_SERVICE_URL" --token-file "$OWNED_TOKEN_FILE" \
  --firmware "$MONITOR_PROBE_BIN" --out-dir "$OUT/monitor"
```

PM1 runner 从环境读取自有服务的访问凭据。用独立输出目录复跑 `bad-crc` 和 `strap`。USB runner 需要已运行的原版 Bit Pirate 会话。HID 命令需要连接到支持 UART1 H4 的 StickS3 测试 guest。其测试应用以加密读取的 Report Map、Input Report ID 1 和 BtnA 按下/松开构成验证。Wi-Fi 探针用 ESP-IDF v5.5.4 生成 8 MiB merged image，原版 M5Gotchi 对照用 `--stock` 和独立输出目录。运行时、ROM、固件和报告的精确哈希见证据摘要。

## 验证边界与回滚

以上均为虚拟设备结果。原版 AirMouseS3 的原生 BLE 配对、原版 Evil-StickS3 monitor 工作流和任意 raw TX capture 仍未验证。Buffer DMA、USB HID 数据交换和 USB host mode 不在本轮 OTG 结论内。真实 PM1 写入、掉电行为、USB PHY、BLE RF/安全性及 Wi-Fi RF 均为 `NOT RUN`。

本轮只在虚拟设备上执行。复现时使用独立服务，切回先前的源码和运行时绑定即可恢复旧模型。早期失败与后续独立通过均保存在证据摘要。公开版本仅保留哈希、协议结果和脱敏标记。 [执行结果](run.json)
