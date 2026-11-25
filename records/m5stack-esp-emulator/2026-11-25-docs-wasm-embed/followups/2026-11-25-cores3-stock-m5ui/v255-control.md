# 显式 UIFlow2 v2.5.5 的 Switch 原例程

同一官方 Python 原例程在锁定 0046 和同一静态站点上的显式 v2.5.5 CoreS3 工作台通过。该入口使用已批准的 cores3-display 启动环境。固件是 565f1de9c87e8fe12f133e64ae6e3c6d32085c46e52269b864ea1cf4604f0927。测试随后走普通工作台的 Python 文件选择及 UART0 raw-paste，加载同一 ddca9d31feeee60478bacacb32d35275bc110c388924146a90b175eac7b5cc2a Switch/Arc 源码。

- 在平面屏幕可见中心 (158,106) 两次正常点击，原程序按序输出 switch0 checked 和 switch0 unchecked。控制区产生 1,112 个绿色像素，关闭后完整帧 SHA-256 恢复到点击前。
- 盲点 (25,58) 的实际触摸已收到，控制区保持原样。
- 同一会话明确完成编辑器中断，通过页面 Stop 退出 0，CDP 在浏览器上下文关闭前观察到 6 个 Worker 全部正常回收。
- 这次对照验证 Switch。Arc 文档当前指向同一份 Switch 字节，Arc 控件功能由独立问题追踪。Slider 在 v2.5.5 的交互与编辑器中断待验收。 [Arc 文档问题 #133](https://github.com/m5stack/uiflow-micropython/issues/133)

UIFlow2 2.5.3 固定的 CoreS3 M5GFX 面板偏移为 3，默认 rotation 值为 1。原例程明确设置 rotation 为 0 时，旧驱动进入内部旋转 3，同时触摸驱动变换坐标。2.5.5 固定的 CoreS3 M5GFX 面板偏移和默认 rotation 均为 0，原例程在这一版本走自然坐标。旧驱动把真实 FT5x06 输入换算为逻辑坐标 (239−raw_y,raw_x)，与诊断命中的 (106,81) 相符。0046 的 CoreS3 显示面板始终以固定的 320×240 不变换窗口写入来宾像素。当前已验证的最小演示方案是让该原例程通过显式 v2.5.5 入口运行。旧固件任意旋转需要独立的控制器和显示投影修复。 [UIFlow2 2.5.3 依赖树](https://github.com/m5stack/uiflow-micropython/tree/50e440780492aa847378c7d3477ab912f7063bac/m5stack/components/M5Unified) [2.5.3 M5GFX 固定源码](https://github.com/m5stack/M5GFX/blob/9bcedf4e19d4cab7a0793de0598ae5390b4689fe/src/M5GFX.cpp#L590) [旧 LCD 旋转和 MADCTL](https://github.com/m5stack/M5GFX/blob/9bcedf4e19d4cab7a0793de0598ae5390b4689fe/src/lgfx/v1/panel/Panel_LCD.cpp#L125) [旧触摸坐标变换](https://github.com/m5stack/M5GFX/blob/9bcedf4e19d4cab7a0793de0598ae5390b4689fe/src/lgfx/v1/panel/Panel_Device.cpp#L500) [旧 UIFlow2 LVGL 读回](https://github.com/m5stack/uiflow-micropython/blob/50e440780492aa847378c7d3477ab912f7063bac/m5stack/components/M5Unified/mpy_lvgl.txt#L189) [2.5.5 M5GFX 固定源码](https://github.com/m5stack/M5GFX/blob/21213080fba00c675d5dcca0ef2abd4b349e3cef/src/M5GFX.cpp#L455)

与 [v2.5.3 原结果](report.md) 分开记录。 [精确机器证据](evidence/stock-m5ui-v255-control.summary.json) [实际回放脚本](code/run-v255-switch-0046.mjs)
