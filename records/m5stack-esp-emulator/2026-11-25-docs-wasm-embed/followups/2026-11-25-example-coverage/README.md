# CoreS3 和 Cardputer-Adv 文档例程的 WASM 覆盖

- 日期 `2026-11-25`
- 结果 `PARTIAL`
- 工作类型 `report`
- 来源 [CoreS3](https://docs.m5stack.com/en/core/CoreS3) · [Cardputer-Adv](https://docs.m5stack.com/en/core/Cardputer-Adv) · [官方 UIFlow2 SDK](https://github.com/m5stack/uiflow-micropython)
- 源码 文档 `6ee4f2fb…f1a`，UIFlow2 `a61a2940…95b6`，模拟器基线 `afd1c635…1243f3`
- 环境 桌面 Chrome 158.0.8127.37、macOS，正式文档负控和隔离浏览器 WASM 虚拟设备验证

CoreS3 和 Cardputer-Adv 能做精选图形、触摸和键盘示例。正式文档嵌入还需要共享内存配置。默认路径下，26 个 Arduino 例程均启动，4 项完整通过。CoreS3 四个 ESP-IDF BSP 例程均进入应用且没有画面。UIFlow2 盘点了 208 个板型 Python 示例和 2 个 Blockly 工程，99 个 Python 示例实际进入浏览器来宾检查。

- [结论与范围](report.md)
- [执行记录](run.json)
- [Arduino 逐例矩阵](evidence/arduino/README.md)
- [UIFlow2 索引和未运行边界](evidence/uiflow2-index.summary.json)
- [窄屏布局与输入就绪时序](evidence/embed-ux-summary.json)
- [UIFlow2 逐例结果 1](evidence/uiflow2-cases-01.summary.json)
- [UIFlow2 逐例结果 2](evidence/uiflow2-cases-02.summary.json)
- [UIFlow2 逐例结果 3](evidence/uiflow2-cases-03.summary.json)
- [UIFlow2 逐例结果 4](evidence/uiflow2-cases-04.summary.json)
- [UIFlow2 逐例结果 5](evidence/uiflow2-cases-05.summary.json)
- [UIFlow2 逐例结果 6](evidence/uiflow2-cases-06.summary.json)
