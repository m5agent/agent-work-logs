# M5TabOS 0.9.1 在最终 Device Service 1.91 的原版复验

- 日期为 2026-11-18，结果为 PASS，范围是启动出帧和一次原生触摸。
- 环境为隔离 Device Service 1.91.0、Tab5 原生 esp-emu 1.1.0、ST7123 完整部件，属于虚拟设备验证。
- 最终源码为 `c7e25be5410d3a9968107bc7a0cab5acb9d708bc`。固件、运行时和部件身份见回执。

按固件哈希选用 ST7123，得到 16 张完整画面，其中 15 张非黑。点击欢迎页的下一步后进入时区页，来宾消费了按下和抬起各一份报告。[完整报告](report.md) · [执行清单](run.json) · [回执](evidence/final-191-board-touch.summary.json)
