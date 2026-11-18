# Nesso N1 原版 RFID 看门狗与横屏复验

- 日期为 `2026-11-18`，时区为 Asia/Shanghai
- 结果为 `PARTIAL`
- 工作类型为 `issue`
- 问题来源为 [公开 issue #216](https://github.com/m5agent/m5stack-esp-emulator/issues/216)
- 源码版本为 `0e376abc91ddf8252eb565cb1b54204be8e1f089`
- 环境为 隔离 Device Service 1.89.0 和原生 ESP32-C6 QEMU

## 结论

原版稳定性仍为 FAIL。第二轮确认 90 秒重配返回 0x103 后，未喂狗的 IDLE 在原有 5 秒窗口触发中断。离线横屏检查未出现回归。

## 关键证据

- 150.021 秒无追踪控制有一次非请求重启。
- 两次 UART 等待均在看门狗前按时返回，未执行 RFID 读卡。
- 两份离线方向转换结果分别与历史 PNG 哈希相同。

## 文件

- [完整报告](report.md)记录执行步骤、观察与限制。
- [运行清单](run.json)记录输入身份与各层判据。
- [有界证据](evidence/README.md)记录脱敏范围和原始产物哈希。
- 补丁和测试工程不适用。本条记录沿既有执行路径进行复验。

## 未覆盖项

在线 display-orient 路由、RFID 读卡、浏览器和实体设备均为 NOT RUN。
