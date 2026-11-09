# StickS3 原生功能交付与复测

PR #210 在精确 head 560005a20dc3e29d826561856ab58e21b10f2d79 的平台与网络隔离检查通过后合并。主分支合并提交 f4f076c2e07f727ce9ae23ddfa6ba7211f1b967e 的 CI 通过。原版 Bit Pirate 以可复现的枚举和 CDC 实际数据交换验收，#202 已关闭。 [PR #210](https://github.com/m5agent/m5stack-esp-emulator/pull/210) · [main CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42592653226) · [#202 验收](https://github.com/m5agent/m5stack-esp-emulator/issues/202#issuecomment-6736528226)

122 层合并候选的 5 项 StickS3 UIFlow2 外设回归通过。SDK Wi-Fi 探针和原版 M5Gotchi 分别在此运行时复跑，正负对照均通过。原版 Evil 的扫描列表观察继续绑定 121 层运行时。

相同原版 PM1 和 122 层 QEMU 的无跟踪直接对照中，多线程和单线程 TCG 分别有 1/2、2/2 次取得完成标记。两组均保留两颗虚拟 CPU。单线程 Device Service 的原版矩阵与坏 CRC 对照通过，三次并发原版 IAP 中有两次取得完成日志，一次写入校验完成但仍缺最终标记。单线程调度是局部诊断条件，PM1 完成稳定性仍待修复。 [直接对照](evidence/direct-hwcdc-scheduling-summary.json) · [服务复跑](evidence/service-hwcdc-repeat-summary.json)

#201、#203 和 #204 仍开放，后续分别验证 PM1 终态、原版 AirMouseS3 原生 BLE、Evil 混杂模式与完整原始帧数据。
