# Spirit Level 原版标准审核的 GPIO41 送达复验

[前序 Reviewer 0.29 运行](../../README.md)已通过启动与画面验证，描述中的屏幕按压仍需人工复核。此次用同一份 609,856 字节的 Spirit Level v1.0.0 完整原版、原描述及默认审核设置运行保存快照重试。候选 Reviewer 0.29.1 把 AtomS3 显示组件的按压描述映射为实体 BtnA。Device Service 1.99.3 使用精确签名的 `m5atoms3-st7735` 原生 QEMU，保留同一原版应用区域和 8 MiB 规范化 Flash。两个服务以及 ROM、QEMU 和 API 的完整身份见[证据摘要](evidence/atoms3-spirit-reviewer-0291-typed.summary.json)。

标准请求路径为 `POST /api/reviews/{id}/retry`，提交保存快照、关闭 Burner 提交。Device Service 会话通过 `POST /api/v1/sessions/{id}/wait` 返回 HTTP 200，启动无需输入解锁首帧，随后在 60.010 秒采样 13 次。使用 `POST /api/v1/sessions/{id}/input` 提交三个类型化按钮动作，HTTP 均返回 200。虚拟队列与 QEMU GPIO41 原生轨迹合并核验了同会话三组低高边沿。

| 标准计划动作 | 请求虚拟时长 | 请求受理和 GPIO41 低高边沿 | 动作前后帧哈希 |
| --- | --- | --- | --- |
| `click_a` | 120 ms | 已记录 | 变化 |
| `hold_a_0_6` | 600 ms | 已记录 | 一致 |
| `hold_a_2_2` | 2200 ms | 已记录 | 变化 |

虚拟计时回执的 `queued` 描述输入排队，GPIO41 轨迹补足送达证据。原生轨迹保留次序，本次未从轨迹推导来宾内部防抖后的有效时长。标准运行保留一张 128×128 的常规 TUBE 画面，其原始 PNG 和同会话 ZIP 中的 PNG 完全一致。动作原始 JSON 保留逐项哈希，归档未留存所有逐项 PNG。审核仍为 `manual_review / SIM_PARTIAL / E_INTERACTION_CLAIM_PARTIAL`，未用帧哈希变化给切换、归零或重置的业务状态定级。其他时长的带倾斜对照见[独立 GPIO41 验证](../2026-11-19-atoms3-spirit-gpio41-hold-timing/README.md)。

采集器首次总摘要为 `INCOMPLETE`，原因是用对象身份断言布尔值 `False`，而 SQLite 终值为整数 `0`。终态、就绪、动作和证据 ZIP 当时已写出。独立离线回读核对了原始报告里的终态、请求状态、三项动作和实际边沿，保留最初摘要与原始回执哈希。ZIP CRC 和 8 项成员哈希均验证通过，Flash 应用区逐字节与原版对应区间相同。

访客与独立服务退出，停止历史保留，释放 Flash 后读取返回 `flash_not_available`，活动租约归零。本轮未运行实机、浏览器、访客网络、常驻审核端或独立固件状态断言。Burner 未提交。公开记录仅包含脱敏派生结果和原始证据哈希、长度，省略原始包、作者描述、端点和独有标识。 [脱敏证据摘要](evidence/atoms3-spirit-reviewer-0291-typed.summary.json)
