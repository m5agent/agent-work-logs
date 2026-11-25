# 完整报告：review-sta 上线后的复跑与人工来源

## 1. 背景

2026-11-24 模拟器/审查服务上线了 `review-sta` 便携网络 profile：`qemu-wifi` 同 guest、
userspace fixture-only、不依赖 Linux 网络命名空间，支持 DHCP/DNS/HTTP/TCP/UDP/MQTT
fixtures、setup inputs 和 pcap。理论上它应该消掉之前 7 条 `worker_namespace_unavailable`。

用户反馈“做完的审查记录里还是有大批设备需要人工复核”。本次复跑最近的网络和交互任务，
确认当前真实状态。

## 2. 最近 45 条总览

窗口：2026-11-23 00:00 至 2026-11-25 09:35 +08:00。

| 状态 | 数量 |
| --- | --- |
| `done/SIM_VERIFIED` | 11 |
| `manual_review/SIM_PARTIAL` | 31 |
| `failed` | 3 |

人工构成：

| 错误码 | 数量 | 说明 |
| --- | --- | --- |
| `E_NETWORK_NO_ACTIVITY` | 10 | review-sta 窗口内没有 Wi-Fi 初始化/扫描/关联 |
| `E_INTERACTION_CLAIM_PARTIAL` | 7 | 应用输入/显示时序 |
| `E_EVIDENCE_UNAVAILABLE` | 5 | Tab5 无匹配 ELF，无法取帧 |
| `E_NO_SIM_PROFILE` | 4 | PaperColor、TimerCam、原版 M5Paper ×2 |
| `E_NO_FRAME` | 2 | Cardputer 应用无首帧 |
| `E_NETWORK_PARTIAL` | 1 | StopWatch exact lane 有 DHCP，无 TCP/UDP |
| `E_SIM_APP_READY_PARTIAL` | 1 | AtomLite 无屏幕 |
| `E_SIM_MODEL_GAP` | 1 | Tab5 Quansheng K1 重复启动 |

网络仍是最大单一类别（11/31 ≈ 35%），但“基本都是网络”不准确：Tab5 取帧 5 条、
机型档案 4 条、交互 7 条、无首帧 2 条、显示less 1 条、模型 gap 1 条。

## 3. 11 条网络复跑结果

| 任务 | 固件 | 复跑结果 |
| --- | --- | --- |
| `job-26c58bb067d3` | Monster for Cyberspace.online | `E_NETWORK_NO_ACTIVITY` |
| `job-6df3d35e88bd` | 玄机OS | `E_NETWORK_NO_ACTIVITY` |
| `job-37bb82f2046c` | SecTrustKey | `E_NETWORK_NO_ACTIVITY` |
| `job-de1d1429c30c` | SecTrustKey | `E_NETWORK_NO_ACTIVITY` |
| `job-ba218202b8d6` | Bruce CN | `E_NETWORK_NO_ACTIVITY` |
| `job-92abbf2f7c63` | CardOS-zh | `E_NETWORK_NO_ACTIVITY` |
| `job-ce6e88172191` | CardOS-zh（重发） | `E_NETWORK_NO_ACTIVITY` |
| `job-687de4ba2337` | StopWatch Demo Plus | `E_NETWORK_PARTIAL` |
| `job-11c7fdcdb770` | META TV IR | `E_CONTENT_AGENT` |
| `job-eac32bc5d55f` | FlipHack | `E_CONTENT_AGENT` |
| `job-fd6f6d22bd66` | NucleoOS | `E_INTERACTION_CLAIM_PARTIAL` |

**没有新增 `worker_namespace_unavailable` / `board_not_advertised`。** review-sta 的
同 guest、pcap 隔离、fixture 路径均正常；问题变成了“应用没有发起 Wi-Fi”。

### 3.1 no-activity 证据

7 条 `review-sta-network.json` 共同点：

```json
{
  "status": "PARTIAL",
  "failure_codes": ["no_network_activity"],
  "firmware_wifi_stack": true,
  "station_joined": false,
  "setup": [],
  "preset": {
    "requested": {"sd_card": "blank", "saved_station": true},
    "applied": {"saved_station": "no_known_layout"}
  },
  "event_types": []
}
```

pcap 有隔离证明（`pcap_isolation=PASS`），但没有任何 Wi-Fi probe/auth/assoc/DHCP 事件。
这些固件的 Wi-Fi 是菜单/配网功能；`review-sta` 不会替用户点菜单、选 SSID、填密码。
当前 saved-network preset 只有一条源码确认的 layout（CardRadio 的 `mp3net`），所以
几乎所有任务都是 `no_known_layout`。

### 3.2 StopWatch

StopWatch 走的是 exact `generic-observe` lane（不是 review-sta），有 1 次 DHCP DORA、
0 个 TCP/UDP payload flow，所以 `E_NETWORK_PARTIAL`。它已经有 `pre_network_steps`，
但网络功能没有产生数据面；需要单独看 exact lane 或改用 review-sta。

## 4. 7 条交互复跑

Camillia、DeskFolio、CardputerDict ADV、Adviibo、Monster online、Bruce MeshCore 复跑
仍是 `E_INTERACTION_CLAIM_PARTIAL`；Adversary ADV 转 `E_CONTENT_AGENT`。没有新的
交互 PASS，说明剩余交互不是旧记录残留，而是应用/时序问题。
典型：

- DeskFolio：PaperS3 触摸被接受但 E-Ink 画面不变；
- Camillia：Cardputer 键盘探针无画面变化；
- CardputerDict ADV：词典输入/翻页未产生声明变化；
- Monster online：Cardputer ADV 键盘/菜单交互。

## 5. 其他人工

- **Tab5 5 条**：Monster、GPSDO、Overhead Flight Tracker、GRUVPAKT T8 都是
  `screenshot_requires_matching_elf`；Quansheng K1 是 `E_SIM_MODEL_GAP`（重复启动）。
  这是 Tab5 取帧/模型能力，不是网络。
- **无档案 4 条**：PaperColor（映射已补，历史任务无缓存 BIN）、TimerCam（Unit
  CamS3-5MP 未建模）、原版 M5Paper ×2（未建模）。
- **无首帧 2 条**：SMF MIDI Player、Adversary（Cardputer）。
- **AtomLite 1 条**：无屏幕设备仍按首帧判定 readiness。

## 6. 已做修改

- 运行时 `DEVICE_MAP` 增加 `PAPER_COLOR` / `M5STACK_PAPER_COLOR` → `papercolor`。
- `TIMERCAM` 增加明确原因（相机单元未建模）。
- 模拟器 issue #238 评论复跑结论，列出下一步需求。

## 7. 下一步

模拟器：

1. 增加 Wi-Fi 初始化/扫描事件（`wifi_initialized`/`wifi_scan`/`station_start`）；
   没有 AP 事件时返回 `NOT_USED`，不要因镜像里有 Wi-Fi 字符串就判 `PARTIAL`。
2. 扩展 saved-network preset：ESP-IDF `nvs.net80211`、Arduino `WiFiMulti`、
   M5/UIFlow2 等源码确认的布局。
3. `setup_inputs` 同 guest 执行并记录证据；审查服务提供菜单导航序列。
4. StopWatch 走 review-sta；PaperColor/TimerCam/Tab5 补机型或明确 unsupported。

审查服务：

1. 区分核心网络与可选网络：可选网络未尝试标 `NOT_USED/OPTIONAL`，不转人工；
   核心网络未尝试先跑 setup，再决定 PASS/FAIL/人工。
2. StopWatch 路由、PaperColor 映射、Tab5/ELF 边界同步调整。
3. 无屏幕 AtomLite 用串口 readiness。

## 8. 未覆盖项

- Wi-Fi init 事件/saved-network preset/setup 自动化：`NOT RUN`（需求已提）。
- 核心 vs 可选网络策略：`NOT RUN`（需要确认）。
- Tab5 无 ELF 取帧、PaperColor/TimerCam 机型：`NOT RUN`。
- 物理设备复跑：`NOT RUN`。
