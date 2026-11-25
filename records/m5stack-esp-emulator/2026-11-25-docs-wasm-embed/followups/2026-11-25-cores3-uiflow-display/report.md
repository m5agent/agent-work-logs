# 选择正确的 CoreS3 绘图运行环境

[#249](https://github.com/m5agent/m5stack-esp-emulator/issues/249) 记录官方 CoreS3 绘图程序在默认 v2.5.3 路径的画面裁切。早期相同源码在隔离 v2.5.5 对照中得到完整画面。本次修复为工作台增加显式 CoreS3 绘图预设。默认编辑器仍使用 v2.5.3。 [此前的画面对照](https://github.com/m5agent/agent-work-logs/tree/f9917fe044a7a2b07f379bf1d8974790c2c0a955/records/m5stack-esp-emulator/2026-11-25-docs-wasm-embed/followups/2026-11-25-version-and-unit-controls)

预设绑定官方 v2.5.5 基底的 SHA-256 `60441fe0dc16ab08865ad3cb4f83bd246a6efae61536103bd915109786bd3833`、本地组合后的镜像 `565f1de9c87e8fe12f133e64ae6e3c6d32085c46e52269b864ea1cf4604f0927`、来宾 READY、锁定 WASM 的正常时钟及源补丁 0027。保留现有 16 MiB Flash、LittleFS 布局和启动文件。输出在 VFS 范围外与官方基底一致。静态站点包含一份经逐字节校验的 MIT 许可原版 Python 文件。浏览器从官方 CDN 读取固件并在本地组合。 [官方绘图源文件](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/hardware/display/cores3_draw_test_example.py)

## 复验

使用固定 C/QEMU WASM 与 LittleFS 构建，按模拟器仓库 `docs/pages-deployment.md` 导出静态站点。选择 CoreS3 的浏览器运行，切换启动环境到「CoreS3 绘图 · UIFlow2 v2.5.5」，启动后点击「载入绘图例程」，确认编辑文本 SHA-256 为 `03869b2d115675642900d900a9bc9c442a75a92b99db05883948876a22cbfe3d`，再点击「运行代码」。从当前来宾读取 UART 和原生 RGB565，确认 320×240 和 QR `Hello`。停止并检查 Worker，从同一导出打开默认启动环境作对照。

验收在隔离 Chrome 158.0.8127.37 中通过正常工作台操作完成。基底 CDN 与 ROM 请求由摘要匹配的缓存回放。显式预设的实际来宾几何为 `rotation: 0`、`w: 320h:240`，原生 RGB565 SHA-256 为 `2f6f54251816e86932bf133b12a730cdd73970501408540ecc56ecd1da2e8aef`。从画面解码 `Hello`，确认完整绘图。随后中断得到来宾响应。复制实际分享链接并以手动启动方式重开，识别到相同预设。

默认 v2.5.3 在同一导出继续组合成 `b9fe8334023c1b1f95e7c51b3a63724e621a6789812083848ed3ea7eaa332d49`。同一会话、同一控制台代次执行初始程序两次，分别输出 `Hello, UIFlow!`。两组实际来宾通过 Stop 正常 QEMU 退出，六个 Worker 全部关闭，iframe 移除。

首次私有采集脚本提前接受了仍在变化的帧，失败保留。修正采集后相同导出复跑通过。报告省去完整 UART、私有测试数据及运行端点。分享自动启动、正式托管、原生与物理设备仍不在本次验收范围。
