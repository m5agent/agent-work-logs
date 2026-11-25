# review-sta 上线后的复跑：网络不再缺模型，缺的是“应用没发起 Wi-Fi”

- 日期：`2026-11-25`
- 结果：`PARTIAL`（review-sta 后端已生效；11 条网络复跑 0 条转 VERIFIED，根因变为 no-activity）
- 工作类型：`service_debug`
- 问题来源：用户反馈“做完的审查记录里还是有大批设备需要人工复核”
- 源码版本：审查服务运行时 `review_sta_network.py` / `app.py`（2026-11-24 更新）；
  模拟器 `review-sta` 已上线，issue #238 已评论复跑结论
- 环境：macOS arm64；常驻审查服务；本机 Device Service 原生 QEMU；saved-snapshot
  复审 `submit=false`；无真机

## 结论

最近 45 条任务（2026-11-23 00:00 至 2026-11-25 09:35 +08:00）：

| 状态 | 数量 |
| --- | --- |
| `done/SIM_VERIFIED` | 11 |
| `manual_review/SIM_PARTIAL` | 31 |
| `failed` | 3 |

人工构成：

| 错误码 | 数量 | 性质 |
| --- | --- | --- |
| `E_NETWORK_NO_ACTIVITY` | 10 | 应用没有发起 Wi-Fi/扫描/关联；不是网络模型缺失 |
| `E_INTERACTION_CLAIM_PARTIAL` | 7 | Cardputer 键盘、PaperS3 E-Ink、MeshCore 等应用/时序 |
| `E_EVIDENCE_UNAVAILABLE` | 5 | Tab5 只有 BIN、没有匹配 ELF，无法取帧 |
| `E_NO_SIM_PROFILE` | 4 | PaperColor、TimerCam、原版 M5Paper ×2 |
| `E_NO_FRAME` | 2 | Cardputer 应用无首帧 |
| `E_NETWORK_PARTIAL` | 1 | StopWatch exact lane 有 DHCP，无 TCP/UDP |
| `E_SIM_APP_READY_PARTIAL` | 1 | AtomLite 无屏幕 |
| `E_SIM_MODEL_GAP` | 1 | Tab5 Quansheng K1 重复启动 |

所以“基本都是网络”已经不准确：网络 11 条（约 35%），其余 20 条是 Tab5 取帧、机型档案、
交互、无首帧和显示less readiness。网络仍是最大的单一类别，但不是唯一来源。

## 11 条网络复跑

用当前 `review-sta` 复跑之前的 `E_NETWORK_PARTIAL`：

- 7 条转 `E_NETWORK_NO_ACTIVITY`：Monster online、玄机OS、SecTrustKey ×2、Bruce CN、
  CardOS-zh ×2
- 1 条仍 `E_NETWORK_PARTIAL`：StopWatch Demo Plus（`generic-observe`，1 次 DHCP DORA，
  无 TCP/UDP）
- 2 条转 `E_CONTENT_AGENT`：META TV IR、FlipHack（内容审查失败）
- 1 条转 `E_INTERACTION_CLAIM_PARTIAL`：NucleoOS

**没有再出现 `worker_namespace_unavailable` / `board_not_advertised`；`review-sta` 的
同 guest、userspace fixture-only、pcap 隔离都是 PASS。** 也就是说 #238 的便携网络后端
已经生效。

但 7 条 no-activity 的证据都是：

- `firmware_wifi_stack: true`
- `station_joined: false`
- `setup: []`
- `preset.applied.saved_station: "no_known_layout"`
- pcap 零流量

说明**镜像里链接了 Wi-Fi 栈，不等于应用初始化了 Wi-Fi 或发起了扫描/关联**。这些固件的
Wi-Fi 是菜单/配网功能，`review-sta` 提供了虚拟 AP，但不会替用户点菜单、选 SSID、填密码。
当前 saved-network preset 只有一条源码确认的 layout（CardRadio 的 `mp3net`），所以绝大
多数是 `no_known_layout`。

## 7 条交互复跑

Camillia、DeskFolio、CardputerDict ADV、Adviibo、Monster online、Bruce MeshCore 复跑
后仍是 `E_INTERACTION_CLAIM_PARTIAL`；Adversary ADV 转 `E_CONTENT_AGENT`。没有新的
交互 PASS。剩余交互是应用/时序问题，不是统一的解析 bug。

## 已做的修改

- `PAPER_COLOR` / `M5STACK_PAPER_COLOR` → `papercolor` 映射已补（历史任务无缓存 BIN，
  无法原地重跑）。
- `TIMERCAM` 增加明确原因：Unit CamS3-5MP 相机单元尚未建模，该固件是 CardCam 相机端。
- 已在模拟器 issue #238 评论复跑结论，并列出下一步需求（Wi-Fi 初始化事件、saved-network
  preset、setup inputs、StopWatch/PaperColor/TimerCam/Tab5 覆盖）。

## 下一步需求

模拟器侧：

1. 增加 `wifi_initialized` / `wifi_scan` / `station_start` 事件；没有 AP 事件时返回
   `NOT_USED`，不要因为 `firmware_wifi_stack=true` 就返回 `PARTIAL`。
2. 扩展 saved-network preset：ESP-IDF `nvs.net80211`、Arduino `WiFiMulti`、
   M5/UIFlow2 等源码确认的布局。
3. `setup_inputs` 在同一 guest 执行并记录证据，审查服务提供菜单导航序列。
4. StopWatch 走 review-sta；PaperColor/TimerCam/Tab5 补机型或明确 unsupported。

审查服务侧：

1. 区分**核心网络功能**与**可选/菜单网络**：可选网络未尝试时标 `NOT_USED/OPTIONAL`，
   不转人工；核心网络未尝试时先跑 setup，再决定 PASS/FAIL/人工。
2. StopWatch 路由、PaperColor 映射、Tab5/ELF 边界同步调整。
3. 无屏幕 AtomLite 改用串口 readiness。

## 文件

- `report.md`：完整复跑数据、证据与下一步
- `run.json`：结构化记录
- `evidence/review-sta-retry-summary.json`：脱敏后的逐条结果

## 未覆盖项

- 模拟器 Wi-Fi init 事件/saved-network preset/setup 自动化：`NOT RUN`（需求已提）。
- 核心 vs 可选网络策略：`NOT RUN`（需要确认是否实施）。
- Tab5 无 ELF 取帧、PaperColor/TimerCam 机型：`NOT RUN`。
- 物理设备复跑：`NOT RUN`。
