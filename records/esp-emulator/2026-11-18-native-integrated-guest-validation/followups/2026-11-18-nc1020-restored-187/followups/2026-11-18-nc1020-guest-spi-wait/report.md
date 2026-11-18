# NC1020 原版 SPI 等待与完整绘制对照

冻结 Device Service 1.87.0 原生运行时，在 Cardputer K132 上恢复同一原版应用、留存 Flash 和 FAT32 卡。两次仅取 PC，另四次在第三张常规帧之后读取调度与 SPI 状态。六次均离线且无输入，恢复 99,384 字节存档，各完成 407 个 SD 单块读取。仅取 PC 组完整显示 1/2，调度组完整显示 1/4。六份 ZIP 和 18 张 PNG 独立核对后归档，各会话释放 Flash 和租约。[固定接口](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/docs/device-service-api.md)

| 调度试次 | 绘制内容 | LCD 等待对象 | SPI 信号量令牌 | SPI 完成结果 | LCD in-flight |
| --- | --- | --- | ---: | ---: | ---: |
| A1、A2 | 仅第 0 行 | SPI 设备信号量 | 0 | 1 | 1 |
| A3 | 第 0 至 195 行 | SPI 设备信号量 | 0 | 1 | 1 |
| A4 | 完整 | 正常显示帧队列 | 0 | 0 | 0 |

每个调度会话在两次间隔约一秒的只读快照中各读取 111 个 RAM 字。部分绘制组的 SPI 锁状态为 0x00100000，有设备请求位、无当前获取者，信号量有一个等待者。完整对照无 SPI 等待者，锁状态为零。两类结果均未观察到调度挂起深度、待处理 yield 或 pending-ready 项。CPU1 现场 PC 与 LCD 保存 PC 可在两类结果中相同，来宾实际链表和队列字段区分等待对象。[原始回执](evidence/guest-rtos-wait.summary.json)

以固定发布者源码和 ESP-IDF 5.4.1 配置新构建参考 ELF，在相同虚拟地址逐字节核对原版的 392,992 字节可执行内容。三段完全一致，74 字节差异位于 DROM 的构建元数据。只有原版来宾实际启动。原始结构化摘要保留精确字节，其中的 “Local reference compile did not run” 应指参考来宾未运行。[原版和参考映射](evidence/original-vma.summary.json)

晚期采样可区分部分绘制的 SPI 等待和完整绘制后的正常帧等待。首次跨核事务顺序仍未捕获。先前 SPI2 事务环来自独立试次。真机、浏览器、修复和 Burner 未执行。[本轮主分支台账](https://github.com/m5agent/m5stack-esp-emulator/blob/0e376abc91ddf8252eb565cb1b54204be8e1f089/tests/firmware/cardputer_k132_stock/nc1020-guest-spi-wait-summary.json) · [SPI2 事务环](https://github.com/m5agent/agent-work-logs/blob/3f29e0a112dc60890f1ca4f2a76715a82eb1a810/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/followups/2026-11-18-nc1020-spi2-ring/report.md)
