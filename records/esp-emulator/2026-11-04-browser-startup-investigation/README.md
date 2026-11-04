# ESP Emulator 浏览器启动调查

- 日期：`2026-11-04`
- 结果：`PARTIAL`
- 工作类型：`code_change / report`
- 问题来源：用户反馈 Atom Matrix、StickC Plus 在公开页面启动慢，要求检查全部可运行设备。
- 源码版本：`m5agent/m5stack-esp-emulator @ b41eba70eb61f7ddc5c41e0b981341064f9d1d1f`（本记录的已执行基线）
- 环境：Apple M4、系统 Chrome、Metal ANGLE、独占本地静态站与 browser QEMU；不是新的线上 HTTPS 延迟测量。

## 结论

正式发布包 `3c6b2490…` 与原固定 Flash 下，Atom Matrix 点击至 ready 为109.458秒，StickC Plus为90.687秒。两板限定功能和正常Worker清理通过；两个候选均未取得可采用的性能结果。整个19板优化、完整按键、新默认UIFlow工作台和新部署仍未完成。

## 关键证据

- 构建或运行：既有源码构建WASM的两板独立virtual-device基线及候选；新构建不由本记录授予PASS。
- 产物或部署：绑定原正式站点/runtime/source/Flash SHA；没有部署新页面。
- 实机或服务执行：browser virtual-device validation；物理硬件NOT RUN，未使用Device Service。
- 日志、测量或协议：真实guest串口、按键、frame或RMT/QOM、实际CDP Worker退出，详情见summary。

## 文件

- [report.md](report.md)：范围、失败、复现入口及下一步。
- [run.json](run.json)：结构化分层状态。
- [evidence/browser-startup-summary.json](evidence/browser-startup-summary.json)：有界派生摘要，原始报告及执行脚本哈希/尺寸；不含raw帧或Flash。
- `patches/`、`code/`：本阶段不附采用的优化patch；复现使用固定上游检出的既有测试入口。

## 未覆盖项

新74层候选运行时尚待实际guest验证；新默认UIFlow镜像、全部19板按钮/代码执行、逐板提速与正式HTTPS均未由本记录完成。失败候选的正常CDP清理缺证据，保留NOT CAPTURED；ignored附加计时/CDP observer未分发，不将其称为fresh-clone常规检查。
