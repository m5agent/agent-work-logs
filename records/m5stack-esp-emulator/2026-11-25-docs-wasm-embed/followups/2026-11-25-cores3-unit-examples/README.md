# CoreS3 超声波和继电器原例程自动挂接

- 日期 2026-11-25
- 类型 fix，virtual-device validation
- 设备 CoreS3，浏览器 Chrome 158.0.8127.37
- 问题 [模拟器 #246](https://github.com/m5agent/m5stack-esp-emulator/issues/246)

标准工作台按输入固件摘要给两份原例程挂接真实虚拟总线。超声波跟随距离滑块，重复启动恢复 1000 mm。继电器原例程经两次屏幕触摸切换 GPIO 和画面。普通 Display 原例程仍有更新帧且没有 Unit。四次运行都退出并关闭全部 Worker。

- [范围、对照和复现步骤](report.md)
- [结构化执行记录](run.json)
- [控制器计数、输入、实际帧与回收](evidence/standard-workbench.summary.json)
