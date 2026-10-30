# ESP Emulator StackChan / Cardputer Pages 发布与门禁收口

- 日期：`2026-10-30`
- 结果：`PARTIAL`（正式页面已部署；regular all-admitted 远端门禁未通过）；物理硬件 `NOT RUN`
- 工作类型：`code_change` + `service_deploy`
- 问题来源：[PR #65](https://github.com/m5agent/m5stack-esp-emulator/pull/65)
- 页面：<https://m5agent.github.io/m5stack-esp-emulator/>
- 环境：macOS M4；Chrome `156.0.8078.74`；当前 browser QEMU WASM；GitHub Actions Pages

## 结论

PR #65 已合并，正式 GitHub Pages 已更新到包含 StackChan 跳舞 profile 与
Cardputer-ADV canonical 全键映射的网页。最终网页通过 prepared-site 应急流程
部署，部署 job 成功；线上 manifest、Worker finalize wrapper、Cardputer
keymap、QEMU WASM 和 StackChan 精确 Flash profile 均已回读一致。

regular all-admitted 发布没有闭合成 PASS。连续运行发现并修复了三个验收器/
清理问题，但 hosted macOS runner 仍在 Sticks3 完成 normal
`Worker.terminate()`、`fallback=0` 和五个 pthread 关闭后，保留 engine CDP
target graph 条目并阻止部署。为避免把浏览器 bookkeeping 缺陷写成功能 PASS，
本轮使用 prepared-site 应急入口发布，并明确保持 formal publication
`PARTIAL`。

## 关键证据

- 页面部署：
  [run 41058959787](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41058959787)，
  prepare/deploy 均 PASS。
- 静态站 release：
  [pages-preview-20261030-stackchan-dance](https://github.com/m5agent/m5stack-esp-emulator/releases/tag/pages-preview-20261030-stackchan-dance)。
- 发布包 SHA256：
  `ad0607f01cac1b7d313b21a1cd339341156f36535bfc5cbca0e21e5206757026`。
- 线上 manifest SHA256：
  `3c3cdb2f3ea71b458d48c9b6203282ee14bc205e9edad257cb955094c24a958b`。
- QEMU WASM：
  `5d6c36bdafc1129c2652b5ba9422f3deb5ab170475748cea96fdc4cf9520a993`。
- 本机真实浏览器：StopWatch `24/24`、Sticks3 `25/25`；两者 engine target
  均在 iframe 移除前关闭。
- StackChan `c854d3ac…04542`：`11/11`，yaw `307..613`、pitch `677..850`。
- Cardputer-ADV `4faaccde…2bd7b`：`36/36`，56/56 物理键。
- regular 失败保留：
  [run 41056051554](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41056051554)，
  Sticks3 `engine-and-created-pthreads-close-after-iframe-finalization`。

## 文件

- `report.md`：发布、门禁迭代、线上回读和边界。
- `run.json`：结构化结果。
- `evidence/summary.json`：机器可读脱敏摘要。

## 未覆盖项

- regular all-admitted hosted macOS 发布仍为 `PARTIAL`。
- 线上 CoreS3 guest 复测因 M5Burner composer 上游 HTTP 503 `NOT RUN`。
- 物理 StackChan、实体舵机、Cardputer 键盘、机械、电气、LCD 光学和 RF 均
  `NOT RUN`。
