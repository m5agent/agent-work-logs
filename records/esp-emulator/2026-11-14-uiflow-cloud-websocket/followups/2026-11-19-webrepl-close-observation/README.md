# UIFlow2 WebREPL 断开方向与分层心跳

- **日期** 2026-11-19（UTC+08:00）
- **结果** PASS（历史抓包的 API 和界面回放）
- **工作类型** code_change
- **问题来源** 既有 CoreS3 授权连接与未绑定重连的故障记录。[原调查](../../report.md)
- **源码** Device Service 1.99.4。[候选源码](https://github.com/m5agent/m5stack-esp-emulator/commit/a1066b0d4da60e28c63addaf93103f6713e3f8c4)
- **环境** macOS 上的两套独立 Device Service，Chrome 157.0.8103.79，CoreS3 原版留存抓包

## 结论

三份抓包经过正常 API 读取和实际浏览器历史卡片后，均保留配对观测并按连接区分文字心跳和控制帧 Ping/Pong。未绑定路径显示对端先发 TCP FIN，授权超时路径显示设备先发 TCP FIN。授权重连后仍可查看上一次断开的证据。

## 关键证据

- [基线 API 与浏览器回放](evidence/baseline-replay-summary.json)
- [候选 API 与浏览器回放](evidence/candidate-replay-summary.json)
- [独立匿名宿主探测](evidence/anonymous-upgrade-summary.json)

## 文件

[完整报告](report.md) · [结构化记录](run.json) · [证据摘要](evidence/)

## 未覆盖项

本轮为留存虚拟设备证据回放。新来宾、授权云端长连接、物理硬件、远程代码执行、常驻切换和 Burner 发布均未执行。公网匿名探测只覆盖无设备身份的传输入口。
