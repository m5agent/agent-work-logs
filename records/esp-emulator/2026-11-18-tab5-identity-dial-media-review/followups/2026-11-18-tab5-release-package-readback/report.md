# Tab5 CarPlay 原版发布包复核

Device Service 源码为 `929dbf749e4a8ecd6c469fce8aea44120febd03f`，Reviewer 源码为 `5807a7890aca0a6a0cdb2dcc399e96599114786a`。目标是用相同的原版 CarPlay 固件，验证该发布版本组合的原生 Tab5 取帧路径。复跑通过隔离的 Firmware Reviewer 保存快照和 Device Service 会话执行，使用 ST7123 配置。

60.007 秒内取得 13 个 PNG 采样。末帧为 720×1280、48 色，921,600 个像素均为非黑，末帧与较早 GT911 正控的 PNG 逐字节一致。本次没有录到 DSI 取帧 409。独立检查逐项校验了同会话 ZIP 的六个成员、4,151 字节 UART 和最终画面。原生画面通过，整单仍为 `SIM_PARTIAL` / `E_INTERACTION_CLAIM_PARTIAL`。会话和 Flash 已释放，测试服务已退出。 [原版复跑摘要](evidence/carplay-exact-candidate.summary.json) · [较早 GT911 对照](../2026-11-18-tab5-frame-admission/)

发布包的两个 OpenAPI 文件与对应源码逐字节相同。隔离启动报告 36 个目录型号，其中 33 个可创建。浏览器静态清单包含 2,178 项。远端 GitHub CI 平台合约与命名空间策略均通过，最终 Reviewer 本地测试 234 项通过。 [发布包摘要](evidence/release-package.summary.json) · [GitHub CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44197101530)

Browser-WASM guest、物理设备和 Burner 提交未执行。
