# 完整报告：可选网络未使用不再转人工

## 1. 问题

审查框架的旧逻辑：

```text
描述出现 wifi/network/联网 → network_required = true
→ review-sta 窗口内应用没有发起 Wi-Fi
→ E_NETWORK_NO_ACTIVITY → manual_review
```

这会把两类完全不同的固件混在一起：

- 核心联网应用（Monster online、NucleoOS web desktop、CardOS 网络电台、Bruce WiFi 工具）；
- 网络只是可选/次要功能的应用（词典在线发音、HID 鼠标的 Wi-Fi 修复说明、时钟对时、
  离线占卜 + 手机配网）。

后一类应用主功能离线可用，不应该因为“没点开 Wi-Fi 菜单”就整包转人工。

## 2. 策略

新增 `network_optional` 分类：

- 只有明确可选/次要语义才算可选：
  - `optional Wi-Fi`、`used only for the clock`、`only for`；
  - 在线发音、音频缓存、离线 + 配网；
  - changelog 中的 `Wi-Fi fix`；
- 核心功能标记优先，出现以下内容时一律按必验处理：
  - Web desktop / desktop in your browser；
  - Web/HTTP server、network client、client for、social network；
  - Web config、remote desktop、network radio、网络电台；
  - WiFite、dual-band、deauth。
- `optional_network_unused()` 只在以下条件全部满足时放行：
  - `network_optional=true`；
  - review-sta 状态为 `PARTIAL`；
  - `failure_codes` 含 `no_network_activity`；
  - `event_types` 为空（没有扫描/认证/关联/DHCP）。
- 放行时把网络记 `NOT_USED（可选网络未使用）`，不产生阻塞 reason；
- 如果出现任何 AP 事件或失败码，仍按 `FAIL` / `manual_review` 处理，不能用可选标记
  掩盖真实故障。

## 3. 代码位置

- `service/app.py`
  - `NETWORK_CLAIM_TERMS` 增加 `配网`（手机配网是明确网络功能）；
  - `network_claim_optional()` / `optional_network_unused()`；
  - `review_claims()` 返回 `network_optional`；
  - review-sta outcome 后、报告快照前规范化 `NOT_USED`；
  - 核心 no-activity 文案改为“需要应用内配网或 setup 输入”。
- `service/review_sta_network.py`
  - `NOT_USED` 语义补充“可选网络未使用”；
  - `network_label()` 输出 `NOT USED（可选网络未使用）`。
- `service/README.md` 更新判定表。
- `tests/test_review_claims.py` 增加可选/核心分类和 `optional_network_unused` 测试。

## 4. 复审证据

| 任务 | 固件 | 结果 |
| --- | --- | --- |
| `job-4858a2e7bcb8` | Hrenomysh | `done`；网络 `NOT_USED`；pcap 隔离 PASS |
| `job-37bb82f2046c` | SecTrustKey v1.2.0 | `done`；网络 `NOT_USED` |
| `job-de1d1429c30c` | SecTrustKey v1.2.1 | `done`；网络 `NOT_USED` |
| `job-6df3d35e88bd` | 玄机OS | 网络解除；剩交互 |
| `job-fc77011a18b2` | CardputerDict | 网络解除；剩交互 |
| `job-26c58bb067d3` | Monster online | 仍 `E_NETWORK_NO_ACTIVITY`（核心） |

最近 45 条：

| 指标 | 修改前 | 修改后 |
| --- | --- | --- |
| done | 11 | 14 |
| manual | 31 | 28 |
| network manual | 11 | 6 |

网络人工剩余：Monster、Bruce ×2、CardOS ×2、StopWatch。前 5 条是核心网络未发起
Wi-Fi；StopWatch 是 exact lane 有 DHCP 无 TCP/UDP。

## 5. 测试

```text
python3 -m unittest discover -s tests -v
Ran 365 tests
OK
```

新增覆盖：

- 可选：在线发音、音频缓存、clock-only Wi-Fi、离线+配网、`optional WiFi cloud sync`；
- 核心：web desktop、social network/web server、WiFite 工具、网络电台；
- `optional_network_unused` 必须无 `event_types`，FAIL 不放行。

## 6. 剩余项

- 核心网络 no-activity：Monster、Bruce、CardOS；需要模拟器 saved-network/setup 能力，
  或应用内配网导航。
- StopWatch exact lane：有 DHCP 无 TCP/UDP；需要单独看 exact profile。
- Tab5 5 条取帧、PaperColor/TimerCam/M5Paper 4 条无档案、交互 9 条、无首帧 2 条、
  AtomLite 1 条：不在本单范围。
- 物理设备复跑：`NOT RUN`。
