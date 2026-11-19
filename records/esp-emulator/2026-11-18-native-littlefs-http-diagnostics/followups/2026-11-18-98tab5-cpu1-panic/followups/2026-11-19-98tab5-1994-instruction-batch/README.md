# Tab5 98TAB5 1.3.0 原版复位与 P4 指令批量对照

- 日期：2026-11-19
- 结果：FAIL（原版无卡冷启动）；对照与取证完成
- 工作类型：report / virtual-device validation
- 来源：[早期原版 CPU1 启动现场](../../README.md)
- 环境：macOS arm64，Device Service 1.99.4，官方 esp-emu 1.1.0，Tab5 GT911/ILI9881C

三次独立无卡冷启动都执行到原版应用偏移 `0x10000`，DSI 连通后均无完整帧。
默认与显式 50,000 指令批量在 50 秒内各复位 26 次，UART 全部字节一致。
P4 改为 5,000 后复位 56 次，完整保留了前两轮串口作为前缀。

- [环境、对照与关闭条件](report.md)
- [结构化记录](run.json)
- [三次冷启动摘要](evidence/instruction-batch-summary.json)

三轮均取得并校验证据 ZIP，随后释放可写 Flash、租约及 P4/C6 来宾。
带盘、应用输入、浏览器 WASM 和真机未运行。Burner 未提交。
