# M5TabOS 原版使用显式触摸计划复审

## 同源对照

两轮保存快照复审使用同一个 M5TabOS 0.9.1 发布 BIN。两轮运行在同一个冻结
Device Service 1.91.0、Reviewer 0.22.0 和原生 esp-emu 1.1.0 的 Tab5 ST7123
配置。服务保留原有固件准入，并为这份原版规范化 Flash 指定 ST7123。运行中
没有上传 ELF 或修改应用字节。原有复审历史按只读方式取得输入。

| 输入 | 真实观察 | 复审终态 |
| --- | --- | --- |
| 默认中心点击和左滑 | ST7123 接受点击 `(360,640)` 与滑动 `(540,640) → (180,640)`。两次操作的画面均未变化 | `manual_review / SIM_PARTIAL / E_INTERACTION_CLAIM_PARTIAL` |
| 显式 `touch_welcome_next` | 在面板 `(530,1147)` 点击。控制器报告 2 次，确认 2 次。欢迎页和时区页的标题区域分别匹配预期 RGB SHA-256，完整交互前后 PNG 与同版本 Device Service 直测逐字节相同 | 触摸计划 `PASS`。全部审核为 `manual_review / SIM_PARTIAL / E_NETWORK_PARTIAL` |

两轮均获得 720 × 1280 的原生 DSI 画面，各观察约 60 秒和 13 个采样点。
证据 ZIP 的 CRC、六个清单成员的 SHA-256 以及同会话固件身份均已校验。
停机后保留会话历史，释放临时 Flash，最后无活动租约。 [配对结果及完整哈希](evidence/paired-reviewer-touch.summary.json)

## 复现

在隔离服务中使用同版 Reviewer 保存快照，对已持有的同哈希发布 BIN 发起
`POST /api/reviews/{id}/retry`，发送 `sourceMode=saved_snapshot` 和
`useAgentReview=false`。第一轮使用默认输入。第二轮在 `validation.touch_plan`
声明 720 × 1280 面板、空的 `button_bindings`、一步
`touch_welcome_next` 和 12 秒超时。

显式动作的裁剪区域 `[32,104,656,142]` 使用两个已验证原版直测帧的精确
RGB SHA-256。该区域包含页面标题，顶部状态图标位于区域外。Reviewer 先用
`GET /api/v1/sessions/{id}/frame.png?orient=panel&max_age_ms=0` 等待
预期起始区域，再用 `POST /api/v1/sessions/{id}/input` 发送实际点击并比较
结束区域。预期输入、区域哈希与实际回执见 [配对证据](evidence/paired-reviewer-touch.summary.json)。

本轮覆盖欢迎页进入时区页的单个离线动作。网络、配网、实体硬件、其他页面和
Burner 提交均未执行。原始固件、会话标识和画面留在验证环境。
[固定 Device Service 源码](https://github.com/m5agent/m5stack-esp-emulator/commit/c7e25be5410d3a9968107bc7a0cab5acb9d708bc)
