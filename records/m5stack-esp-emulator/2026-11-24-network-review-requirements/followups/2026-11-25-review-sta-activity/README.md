# review-sta 驱动初始化与条件步骤（2026-11-25）

承接 #238 审查服务侧反馈：复跑 11 条网络任务后 7 条为 `E_NETWORK_NO_ACTIVITY`。

## 变更

- 模拟器 PR #241（main `afd1c635f`，API 1.102.0）：`/network` 增加 `wifi_initialized` 与 `reason`。
  ESP32-S3 网卡窗口内来宾从未配置 Wi-Fi MAC DMA 时判 `NOT_USED`（`wifi_not_initialized`）。
  向 `0.0.0.0` 的 UDP（域名解析失败后的 SNTP）记为 `unroutable_dropped`，不再算出站。
  `setup_inputs` 步骤支持 `until=joined`。
- 审查服务（main `ecb51fb`）：Cardputer 系列在没有显式配网步骤时发送有界 Enter 导航探针（`setup_source=probe`），
  探针窗口结束前不做交互探测；`wifi_not_initialized` 对可选网络按 NOT_USED 处理，核心网络仍转人工。

## 结果（Cardputer ADV，virtual-device validation）

| 固件 | 结果 |
| --- | --- |
| Bruce CN 1.17-zh | 入网、租约、pcap 隔离 PASS，审查 `done / SIM_VERIFIED` |
| CardOS-zh V6.2 | 同上；NTP 域名记为外部依赖 |
| CardRadio | 保持 `done / SIM_VERIFIED` |
| Monster for Cyberspace 3.0.2 | 仍转人工：关联并发 DISCOVER，收到与 CardOS 相同的 OFFER 后不发 REQUEST，原因未查明 |

常驻 18853、8790、8787 已切换到 `…-main-1102-review-sta-activity-20261125`，历史保留。
生产 dry-run（submit=0）三个任务均为 `done`，未提交 Burner。

## 边界

探针只证明固件能入网，不证明应用功能。经典 ESP32 网卡没有驱动初始化信号，Core2 与 StickC Plus2 仍判 `PARTIAL`。
物理硬件、browser-WASM、WPA3、真实 TLS 为 `NOT RUN`。
