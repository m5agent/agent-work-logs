# CoreS3 原版 M5UI 触摸复验

- 日期 2026-11-25
- 问题 [模拟器 #255](https://github.com/m5agent/m5stack-esp-emulator/issues/255)
- 结果 PARTIAL，浏览器虚拟设备验证

Switch 显示正常。标准平面画面的可见中心点击未触发。诊断点击改送原始坐标 (106,81)，同一原程序按序输出 checked、unchecked，真实画面同步变色。Slider 的正常拖动改变了滑轨和数值，画面可见 25→40，随后编辑器中断超时。两者都经页面 Stop 正常结束。Arc 的文档示例源码与 Switch 逐字节相同，合并记录。

- [报告和复现](report.md)
- [运行记录](run.json)
- [机器证据](evidence/stock-m5ui.summary.json)
- [摄像头 QR 后续计划](code/camera-qr-plan.md)
