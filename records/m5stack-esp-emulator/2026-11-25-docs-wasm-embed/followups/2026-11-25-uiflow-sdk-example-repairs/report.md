# CoreS3 ADC、GPIO、WDT 与 UART1

从同一静态浏览器工作台打开 CoreS3。将官方文档链接的四份原始 Python 例程分别送到来宾，确认源码哈希和 REPL 传输。ADC、GPIO、WDT 由于 `from hardware import *` 未取得对应的延迟导出而报告 NameError。UART 将整数传入 `UART.write`，来宾报告需要缓冲区协议。

候选在三个示例中显式导入 API，UART 将计数文本编码为字节，并修正文档中的 UART 导入拼写。重跑采用同一 CoreS3 编程镜像 `b9fe8334023c1b1f95e7c51b3a63724e621a6789812083848ed3ea7eaa332d49` 和同一 Xtensa WASM `96c7f8baf1d5f2fd760c560a0827ef7305ad06a1cefb28c905d05d796dc540d8`。

- ADC 读出模拟值 `ADC Value:2048`，GPIO 例程输出 GPIO6 和 GPIO7 的不同状态。这组验收覆盖原程序获取值、周期循环和屏幕更新。
- UART1 原例程通过写入进入正常的间隔循环。实际 RX 回显需要 UART1 对端。
- WDT 在无输入时显示 `Not Feed`，串口报告 `mpy_machine_wdt`，本次有两条实际 RESET 通知。原示例的超时路径可复现。后续编辑器恢复单独跟踪。最终 Stop 退出正常。

脱敏摘要保留独立前后探针、源和运行哈希、来宾标记、帧及清理。真机、真实电气信号和 UART1 接收 `NOT RUN`。
