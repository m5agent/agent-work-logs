# 原生 watchdog 诊断路径

新原生运行时选择性记录第一个 TIMERGROUP1 中断阶段之前的实际喂狗、SYSTIMER 两目标的报警和按核清除、以及相应中断路由。默认关闭。设备服务从同会话本地运行时的有界 stderr 解析版本和形状，放在独立的后台观察里。来宾自身的 panic 字段采用原有读取规则。

测试固定原生 QEMU 和同一份自编探针，同时检查启用和关闭。取证中 CPU0 记录最后一次接受的喂狗，到首次中断阶段约 300.56 毫秒。两个目标均报告报警，CPU1 目标的挂起事件出现合并。探针的实际原生 HTTP 回执、证据 ZIP 与原始此条日志一致，关闭对照无此条记录，两轮均有独立的原版探针 panic。

- [源码复现步骤](https://github.com/m5agent/m5stack-esp-emulator/blob/ee343a14f4097f254d8004967cbbc7c18309573f/tests/firmware/crash_diagnostics/README.md)
- [提交对应 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44095551593)
