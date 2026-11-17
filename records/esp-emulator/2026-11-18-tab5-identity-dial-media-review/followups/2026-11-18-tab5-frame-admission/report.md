# Tab5 原生取帧准入与 Reviewer 观察

## Device Service 元数据

Device Service 1.84.0 候选 `b75853e39afc82b28594b43ce6ffe177de178055` 在 `flash.tab5.frame_capture_admission` 记录符号匹配、原生 DSI 准入、未配置 DSI 或固件摘要未获准入。旧路径缺匹配 ELF 时仍返回原 409 错误，新增已记录的 `error.capture_admission`。已进入 DSI 且缺完整帧则继续返回 `tab5_dsi_frame_unavailable` 和接收器的 `capture_status`。

此字段只描述取帧路径。原生帧仍来自当前会话实际 DSI 数据。同一 CarPlay 原版用于原生取帧和缓存边界，官方 UserDemo 用于原生和旧路径直接比较。98TAB5 的历史复位与缺帧边界沿用前一记录。

## 原版运行的实际回读

CarPlay 准入会话先出现五次接收器已连接但无完整帧的 409，随后于 1.336 秒观察到首个完整帧。该帧有两色和 792,000 个非黑像素；同一会话 ZIP 后续保存实际应用界面，720×1280、48 色、921,600 个非黑像素，内容摘要与此前 CarPlay 启动画面相同。两条帧证据保留各自的采样时刻。 [原版和早期审核回执](evidence/direct-tab5-and-earlier-reviewer.summary.json)

官方 M5Tab5 UserDemo V0.4 使用同一份未修改 BIN 分别测试。准入 GT911 会话在约 34 秒内仅一次启动、零软件复位、无 panic，之后 17 次运行中取帧均为 DSI 已连接但没有完整帧，ZIP 也无 PNG。未准入的同固件会话在约 14 秒内有七次 `screenshot_requires_matching_elf`，携带 `native_dsi_firmware_not_admitted`。原版整体显示仍为 `PARTIAL`，缺帧原因未定位。 [官方发布](https://github.com/m5stack/M5Tab5-UserDemo/releases/tag/V0.4) · [同原版两份证据](evidence/direct-tab5-and-earlier-reviewer.summary.json)

初版 Reviewer `01f2fd57` 的模拟单元用 `tab5` 作为 runtime 值，真实 Tab5 服务回执使用 `qemu`。官方 UserDemo 的已连接 409 因此提前中止观察，实际观察为零秒，分类 `E_SIM_OBSERVATION_INCOMPLETE`。该结果记录为 Reviewer 观察缺陷。早期还有一次保存任务元数据字段错误，在来宾启动前终止。

## 结构化观察与缓存边界

Reviewer `99d5044` 按实际公开会话的 `qemu` runtime 及同会话 Flash 身份核对 Tab5。CarPlay 实际观察 60.012 秒，先有一次接收器已连接的 409，随后取得 12 份 PNG 样本，最终实际应用画面与直接路径一致。该正例覆盖观察方法，单独保留原版整体功能边界。

使用同候选 Reviewer 的较早 UserDemo 保存快照完整观察 60.008 秒，13 次 DSI 已连接但没有完整帧，终态为 `E_TAB5_DSI_FRAME_UNAVAILABLE`。独立 ZIP 串口核对显示该次运行另有一次 ROM `CHIP_LP_WDT_RESET`，在 40–45 秒的采样之间出现，并有两次 ROM 启动横幅。该次终态保留为较早的审核分类。

Device Service `c6a5ab02` 在真实 CarPlay 上拒绝带正数 `max_age_ms` 的共享预览请求，返回 409 `frame_preview_not_available`。默认取帧仍获得 720×1280 的应用画面。 [观察和预览负控](evidence/tab5-observation-and-preview-controls.summary.json)

## 最终原版 UserDemo 保存快照

同一官方原版在 Device Service `c6a5ab02` 与 Reviewer `5807a789` 上完成 60.010 秒串口观察，13 次取帧均为 DSI 已连接但无完整帧。原始 ZIP 同会话串口再次出现一次 `0x10 (CHIP_LP_WDT_RESET)` 和两次 ROM 启动横幅。Reviewer 优先保留复位事实，终态 `E_SIM_WATCHDOG_RESET / guest_failure_observed`，固件归因为 `UNRESOLVED`。缺帧回执同样保留；看门狗触发原因与缺帧原因均未定位。

未准入的同一 UserDemo 原版在旧符号路径以 Reviewer `99d5044` 完成 60.002 秒串口观察。报告保留匹配的 `native_dsi_firmware_not_admitted`，整单为 `E_EVIDENCE_UNAVAILABLE`，该会话只有一次引导且没有 LP 看门狗标记。另一次未准入 CarPlay 在旧运行时较早遭遇模型边界，没有完成安静串口对照。上述有效观察均已停止、Flash 已释放，无 Burner 提交。 [最终和未准入 UserDemo](evidence/tab5-userdemo-final-review.summary.json)

## 发布范围

模拟器主分支为 `929dbf749e4a8ecd6c469fce8aea44120febd03f`。其服务代码和 OpenAPI 与最终实测的 `c6a5ab02` 完全一致。Reviewer 主分支为 `5807a7890aca0a6a0cdb2dcc399e96599114786a`，API 0.16.0。模拟器本地完整套件 2,419 项，跳过 10 项，零失败。Reviewer 234 项通过。准确提交的远程 CI 在归档时尚未完成。 [公开源证据](https://github.com/m5agent/m5stack-esp-emulator/blob/929dbf749e4a8ecd6c469fce8aea44120febd03f/docs/evidence/2026-11-18-tab5-stock-frame-comparison/frame-admission-summary.json) · [准确提交 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44197101530)

实机、浏览器 WASM、常驻切换和 Burner 提交为 `NOT RUN`。
