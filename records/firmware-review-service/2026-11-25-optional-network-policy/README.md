# 审查框架：可选网络未使用不再转人工

- 日期：`2026-11-25`
- 结果：`PASS`（策略生效，3 条网络人工转 VERIFIED，2 条网络问题解除）
- 工作类型：`code_change`
- 问题来源：用户指出“还是有大批设备需要人工复核”，要求修改审查框架
- 源码版本：`firmware-review-service @ 6c4425f`
- 环境：macOS arm64；常驻审查服务；本机 Device Service 原生 QEMU；saved-snapshot
  复审 `submit=false`；无真机

## 结论

审查框架原来把“描述里出现 Wi-Fi/网络”一律视为必须验证；应用没有发起 Wi-Fi 时，
即使网络只是可选功能，也会产生 `E_NETWORK_NO_ACTIVITY` 并转人工。

本次增加 `network_optional` 分类和 `optional_network_unused()` 判定：

- 只有明确的次要/可选语义才算可选，例如：
  - `optional Wi-Fi`、`used only for the clock`、`Wi-Fi fix`；
  - 在线发音/音频缓存、离线占卜 + 手机配网；
- Web desktop、网络客户端、社交网络、WiFite、网络电台等核心功能仍按必验处理；
- 只有“可选 + 窗口内没有任何 Wi-Fi/AP 事件”才记 `NOT_USED`，不阻塞主判定；
- 一旦出现扫描/认证/DHCP 失败，仍按 `FAIL` 或人工处理，不能用可选标记掩盖故障。

## 复审结果

| 任务 | 固件 | 修改前 | 修改后 |
| --- | --- | --- | --- |
| `job-4858a2e7bcb8` | Hrenomysh | `E_NETWORK_NO_ACTIVITY` | **`done/SIM_VERIFIED`**，网络 `NOT_USED（可选网络未使用）` |
| `job-37bb82f2046c` | SecTrustKey v1.2.0 | `E_NETWORK_NO_ACTIVITY` | **`done/SIM_VERIFIED`**，网络 `NOT_USED（可选网络未使用）` |
| `job-de1d1429c30c` | SecTrustKey v1.2.1 | `E_NETWORK_NO_ACTIVITY` | **`done/SIM_VERIFIED`**，网络 `NOT_USED（可选网络未使用）` |
| `job-6df3d35e88bd` | 玄机OS | `E_NETWORK_NO_ACTIVITY` | 网络解除；剩 `E_INTERACTION_CLAIM_PARTIAL` |
| `job-fc77011a18b2` | CardputerDict | `E_NETWORK_NO_ACTIVITY` | 网络解除；剩 `E_INTERACTION_CLAIM_PARTIAL` |
| `job-26c58bb067d3` | Monster for Cyberspace.online | `E_NETWORK_NO_ACTIVITY` | 仍 `E_NETWORK_NO_ACTIVITY`（核心网络，符合预期） |

最近 45 条任务：`done` 从 11 增至 **14**，人工从 31 降至 **28**；网络人工从 11 降至 **6**
（5 条核心 no-activity + 1 条 StopWatch partial）。

剩余 28 条人工：交互 9、Tab5 取帧 5、核心网络 5、无档案 4、无首帧 2、StopWatch 1、
AtomLite 1、Tab5 模型 gap 1。

## 关键改动

- `service/app.py`
  - `network_optional` 分类（`network_claim_optional`）；
  - `optional_network_unused()` 只接受“可选 + 无 AP 事件”；
  - 在报告/检查快照前把这种结果规范为 `NOT_USED`，使网络列与总结一致；
  - 核心网络 no-activity 的文案改为“需要应用内配网或 setup 输入”。
- `service/review_sta_network.py`：`NOT_USED` 说明与标签支持“可选网络未使用”。
- `service/README.md`：更新网络判定表。
- 测试：`python3 -m unittest discover -s tests -v`，**365 项通过**。

## 文件

- `report.md`：完整策略、代码位置、复审证据与剩余项
- `run.json`：结构化记录
- `evidence/optional-network-summary.json`：脱敏后的复审摘要

## 未覆盖项

- 核心网络 no-activity（Monster、Bruce、CardOS 等）仍转人工，需要模拟器 saved-network/
  setup 能力或应用内导航；
- StopWatch exact lane、Tab5 无 ELF 取帧、PaperColor/TimerCam/M5Paper 机型仍未改；
- 交互 9 条仍为应用/时序问题；
- 物理设备复跑：`NOT RUN`。
