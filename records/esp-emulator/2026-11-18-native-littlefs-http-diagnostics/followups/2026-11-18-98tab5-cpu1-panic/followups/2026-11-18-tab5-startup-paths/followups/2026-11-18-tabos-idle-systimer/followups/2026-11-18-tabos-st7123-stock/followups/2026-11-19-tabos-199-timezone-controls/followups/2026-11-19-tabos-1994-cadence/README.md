# Tab5 M5TabOS 0.9.1 原版连续触摸复验

- 日期：2026-11-19
- 结果：PASS（限定 ST7123 原版离线向导）
- 工作类型：report / virtual-device validation
- 来源：[Device Service API](https://github.com/m5agent/m5stack-esp-emulator/blob/2e4ecb1037e38a3d5ce47864aa0cfd54b8c2b858/docs/device-service-api.md)
- 环境：macOS arm64，Device Service 1.99.4，官方 esp-emu 1.1.0，Tab5 ST7123

两轮较短、两轮较长间隔完成时区加减与恢复。第五轮在单独点按加号后持续取帧，
2.22 秒内保持 UTC−2:30。22 次点按均得到实际 ST7123 寄存器读回，并逐项核对
720×1280 DSI 画面标题和时区数值。五次冷启各有一份经校验的会话 ZIP，停机时
均释放可写 Flash、进程和租约。

- [测试方法、取帧边界和历史对照](report.md)
- [结构化记录](run.json)
- [逐次输入、取帧哈希、ZIP 与清理摘要](evidence/native-cadence-summary.json)

1.99.0 的首次加号画面断言失败继续保留，紧接的撤销状态转换不可判定。
本轮没有执行更短间隔、其他 Tab5 板型、联网设置、浏览器 WASM 和真机。
Burner 未提交。此次只做复验，无源码补丁或新部署。
