# 两套常驻 Device Service 的 Tab5 USB 状态回读

本轮上线的是 #226 的能力口径修正。已通过的原版 USB Host 初始化应显示为
`partial`，端点夹具须等实际外设和传输通过后才能公开。
[原版候选验证](https://github.com/m5agent/agent-work-logs/blob/cb240b4d96bfa470ff7aa19926c8c9f74931a418/records/esp-emulator/2026-11-14-p4-v1-originals/followups/2026-11-18-maker-fighter-dwc-self-check/followups/2026-11-18-maker-fighter-host-setup/followups/2026-11-18-tab5-226-usb-host-capability/README.md)

等待工作台、审核执行端和审核队列全部空闲后，核对两套原 Device Service 会话、
Reviewer 历史和抽查证据。在写事务保护下暂停 Reviewer，切换两套 Device Service
并读回，再以同一份 Reviewer 代码和配置启动 Reviewer。应用后和独立重复检查均通过。
正式切换回执时间为 `2026-11-19T00:00:14+08:00`，重复检查完成于本地 00:00:33。

| 角色 | 读回结果 |
| --- | --- |
| 工作台 | Device Service `597e032`，OpenAPI 1.99.0，55 条会话保留，Tab5 USB Host `partial` |
| 审核执行端 | 同一源码与 OpenAPI，94 条会话保留，Tab5 USB Host `partial` |
| Reviewer | `f0101b6`，129 条审核记录一致，抽查的证据 ZIP 一致，重新连接同一审核执行角色后就绪 |

两个设备角色均未公布 USB 端点夹具。Tab5 SD 槽和 UserDemo 音频能力保留，
Cardputer 的 SPI SD 能力保留。Xtensa、C6 和浏览器清单的哈希见证据摘要。
发布阶段没有重跑原版应用或执行真机测试；原版诊断的通过与部分通过边界沿用单独的同固件证据。

原始回执保留在私有状态，公开摘要只保留角色名、计数、版本与哈希。没有提交 Burner，
没有执行回滚。
