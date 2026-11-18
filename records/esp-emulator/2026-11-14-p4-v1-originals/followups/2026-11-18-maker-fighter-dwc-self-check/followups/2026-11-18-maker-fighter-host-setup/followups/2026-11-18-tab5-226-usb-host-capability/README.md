# Tab5 Maker Fighter 1.4 原版 USB Host 能力

- 日期 `2026-11-18`
- 范围 [#226](https://github.com/m5agent/m5stack-esp-emulator/issues/226)
- 结果 **PARTIAL**。原版 USB Host 初始化和事件等待通过
- 环境 Device Service 1.99，隔离的 Tab5 与 C6 伴随运行时，esp-emu 1.1.0
- 源码 `a729e24b1e4724b783ab2d59eec689cfdfeb24b3` 对照及 `6dd68a116a44a9518ca56501ca6ffd212e167bd7` 候选

两轮使用同一原版 Maker Fighter 1.4 及同一规范化 Flash。只读诊断确认原版注册
USB 客户端成功并进入事件等待，DWC 核心标识及 DMA 启用有效，根端口供电且未连接。
候选能力接口报告 `partial`，端点夹具未公布。已核对两个会话的证据 ZIP、来宾字节、
停机和租约释放。

外设连接、HID/MSC 枚举和传输、应用画面及物理硬件均未建立。Burner 未提交。

[详细报告](report.md) · [结构化记录](run.json) · [证据摘要](evidence/usb-host-capability.summary.json)
