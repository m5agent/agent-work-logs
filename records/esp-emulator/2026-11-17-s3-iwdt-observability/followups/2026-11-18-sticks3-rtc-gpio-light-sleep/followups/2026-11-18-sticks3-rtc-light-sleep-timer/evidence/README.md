# RTC 定时器证据

- [SDK 纯定时、组合及拒绝](sdk-timer-and-combined.summary.json)保留旧版、三份候选及每个 GPIO 输入回执。
- [清醒比较器](awake-compare.summary.json)保留相同 BIN 的旧版失败和三份候选通过。
- [挂起复位](reset-rearm-candidates.summary.json)保留两份早期失败以及最终暂停和复位通过的 QMP 和 RTC 寄存器对照。
- [All day watch 原版复验](original-watch-timer-regression.summary.json)保留与已验收 GPIO 路径的独立回归。
- [普通重置 API 回执](device-service-timer-reset.summary.json)记录挂起会话的 HTTP 复位、同一进程身份布尔断言及新启动定时返回。
- [冻结的 1.88 重置复验](device-service-timer-reset-frozen-188.summary.json)绑定最终仓库源码和 RTC 运行时，保留独立 ZIP 与完整事件顺序。

摘要来自同一设备会话的经过验证的串口和 ZIP。运行路径、会话标识、内部地址和设备身份字段已排除。固件、运行时、ROM、安全保留的寄存器值及 raw evidence 的摘要仍可用于核对。
