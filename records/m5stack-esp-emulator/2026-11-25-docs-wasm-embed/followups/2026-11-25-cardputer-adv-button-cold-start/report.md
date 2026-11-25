# 固定原 Button 固件的五次冷启动

在独立 Chromium 进程依次打开同一标准本地导出。每次选择 Cardputer-Adv，上传完全相同的官方 Arduino Button 合并镜像 `07ebcecd82c9a64aad457f5e30eac140bfd24db8006506ea6f04489a860dc0e7`，启动默认 USB CDC On Boot。全量锁定的 0046 浏览器 WASM 为 `210db550d50847a3d4f66d86f81c8d1cdb2ac106ebf6bac16cccc60f4da0e211`，静态站点清单为 `cec271aefa1a575d8b257ea899a8af91eb8209575202fef99fb919bab37f16ac`。每次等待 ROM `entry 0x403c88b8` 后追加 2.5 秒观察，通过真实 F12 控制虚拟 G0。生产运行配置保持 `cardputer-adv-wasm-wallclock`。

| 冷启动 | 实际观察 | QEMU 与浏览器清理 |
| --- | --- | --- |
| 1 | `Button A Pressed` 和 `Button A Released`，CDC +37 字节、+8 包 | exit 0，6 个 Worker 全关闭 |
| 2 | 同上 | exit 0，6 个 Worker 全关闭 |
| 3 | 同上 | exit 0，6 个 Worker 全关闭 |
| 4 | QMP 接受 G0 按下，20 秒内 UART0 和 CDC 仍只有 ROM。事件中没有 RESET | exit 0，6 个 Worker 全关闭 |
| 5 | ROM 已跳转，浏览器报告 QEMU 执行线程异常停止。尚未发送 G0 | iframe 移除，6 个 Worker 全关闭，使用兜底回收，无 QEMU 正常退出码 |

第四次超时后测试仍释放键盘，保留的控制事件仅包含已确认的按下。五次均没有在控制台发现 stack canary 或 Guru Meditation。早前运行的 `ipc1` 症状保留在原记录。此组支持重现 ROM 后无应用输出的症状，另外记录了线程停止，两个失败是否同因仍待确认。测试期间其他进程可能同时编译两个作业。本组样本不能估计发生率或证明主机负载因果。真机未测试。[早前启动记录](https://github.com/m5agent/agent-work-logs/tree/cbb4fd3f9c3a31199f77013049f43be2956efdfa/records/m5stack-esp-emulator/2026-11-25-docs-wasm-embed/followups/2026-11-25-cardputer-adv-usb-cdc) · [五次原报告摘要](evidence/cold-start-summary.json)

## 复现

1. 用 [原 Button 页面](https://docs.m5stack.com/en/arduino/m5cardputer/button) 的代码，以及早前记录固定的 M5Stack Arduino `3.2.5` 和 Arduino CLI `1.3.1` 准备原始和关闭 CDC 的两个对照镜像。回放脚本在启动前严格检查原始源码、输入和填充镜像的 SHA-256。
2. 按 [模拟器源码](https://github.com/m5agent/m5stack-esp-emulator/tree/55d449e345417e4f0b9c6531108f48bdaf8a55db) 的固定配方重建 WASM 0046，使用匹配的 LittleFS 运行物导出静态站点。记录 ROM、运行物与站点 SHA-256。
3. 将 [回放脚本](code/run-public-cardputer-usb.mjs) 放在模拟器根目录下的 `.work` 实验目录。按实际下载位置配置脚本内 `fixtures` 和 `previous` 路径；脚本会验证 ROM、WASM、站点与固件，服务器只绑定随机本地端口。运行 `node run-public-cardputer-usb.mjs SITE on OUTPUT`。每次使用新输出目录且等待 Chrome 进程关闭，再启动下一次。保留超时、执行线程异常和成功的原报告。
