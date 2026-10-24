# ESP Emulator OpenAI 首次启动 NVS 前置条件与状态文档重整

- 日期：`2026-10-25`
- 结果：`PASS`（NVS 根因、fixture 数据面和文档/契约验证）
- 工作类型：`code_change`
- 问题来源：OpenAI Voice Assistant 在无 NVS 配置的虚拟设备 session 中黑屏
- 源码版本：`m5agent/m5stack-esp-emulator @ 3f4bf92b96d5854f0804d7f7014c4a9c244da99e`
- 基线版本：`ec63754f183c7b059fab2d4aa520ab43a307d426`
- 环境：macOS Apple Silicon、Python 3、Node.js、Device Service `/api/v1`、QEMU ESP32-S3；无物理硬件

## 结论

公开 OpenAI AtomS3R 固件的 24 KiB `nvs` 分区整段为 `FF`，应用要求
`config/wifi_ssid`、`config/wifi_password` 和 `config/openaikey`。空 NVS
会令 `main_task` 从 `app_main()` 返回并保持黑屏，因此这不是显示控制器或
NVS 控制器故障。

新增的确定性 NVS fixture 可只覆盖 session Flash 副本。Open-auth 对照完成
WiFi 关联、DHCP、`api.openai.com` DNS 和 TCP/443；WPA2 密码对照读取配置并
触发 authmode threshold，但无法关联当前 Open-auth QEMU AP，登记为
`RUNTIME-05`。

同一轮把 `qemu-wifi/profile=generic-observe` 扩展到任意 ESP32-S3，并重整
当前状态、Backlog、工作流、验证台账、API/OpenAPI 和代码地图。NVS 字段只
接受实际执行 guest Flash 的 `qemu`、`qemu-wifi`、`qemu-ble` 和
`qemu-unified`；`runtime=network` 与 Tab5 明确拒绝。

## 关键证据

- 平台测试：`376/376 PASS`；
- 文档契约：`20/20 PASS`；
- Node SHA256/upload client：`2/2 PASS`；
- OpenAI probe：`13/13` investigation checks PASS；
- GitHub Actions run `40132242654`：`platform-contracts` 与
  `network-namespace-policy` 均 `PASS`；
- 源码固件 SHA256：
  `b3597fcabbff57c98618caa8754af84745e9eac35b2868ab3c4cb0935b7c59b3`；
- 规范化 Flash SHA256：
  `991b1cf328bec7677ed1335d567bfcb7b6c941c1bd6b658eb991b84940b3ce8d`；
- Open fixture SHA256：
  `14f0acc47e1e1bef7e19d29c90febd0fe3707599fd8fc42eeb14dd27cfc26e5d`；
- WPA2 fixture SHA256：
  `ab16f2a1842e40addce0ba26209595fef98d1b3f31113512375d5cfad70fe2bd`；
- Open run effective Flash SHA256：
  `5ca4fb6dc20543a7e2484975cf0a4be9c51c810aa63d8c9105a37347d7220100`；
- Open run pcap SHA256：
  `ab8c5f61077634b7de136e91ea96539c9fb4503ee90a33821058af823edd4295`；
- pcap：`37` packets、`api.openai.com.` DNS query、`1` 个 TCP/443 flow。

## 文件

- `report.md`：根因、实现、当前工作/待办和验证边界；
- `run.json`：结构化记录；
- `evidence/openai-nvs-precondition.redacted.json`：已去除 fixture 配置值拼写的脱敏证据；
- `evidence/verification-summary.json`：测试、CI 和状态契约摘要；
- `patches/`、`code/`：不适用；实现和测试已进入源码仓库。

## 未覆盖项

- 真实 OpenAI 账号、Realtime/WebRTC、语音输入输出和云端成功路径；
- 物理 WPA2/WPA3、RF、功耗和硬件测量；
- 任意 S3 固件在无屏、headless 和云服务场景下的通用结果解释；
- Core2 物理 cache/PSRAM、bit-exact BT controller/baseband 和吞吐/teardown；
- 跨主机 worker executor/reattach、companion/evidence continuity；
- Tab5 缺失的 CSI、I2S/PCM、USB Host、SDIO、动态 I2C 和 ST7123 数据面。
