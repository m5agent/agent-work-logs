# 原生 LittleFS 持久化、Core2 HTTP 与原版诊断

## Core2 与 Nesso N1 跨会话 LittleFS

分别为 ESP32（Core2）与 ESP32-C6（Nesso N1）构建 ESP-IDF v5.5.4 与 LittleFS 1.21.1 探针。构建使用独立输出和 SDK 配置，镜像汇编读取 SDK 的 Flash 元数据。两个镜像为 16 MiB，Core2 bootloader 位于 `0x1000`、使用 40 MHz，Nesso N1 位于 `0x0000`、使用 80 MHz。两者的 `storage` 分区均起于 `0x110000`，长度 1 MiB，块大小 4 KiB。

每块板运行三次。首个来宾从同一确定性种子读取并列举文件，报告 `prior=0`，写入后重新挂载并回读。停止时保留 Flash，重启隔离服务，再从已停止会话导出分区，并独立导入同板的新会话，来宾报告 `prior=1`。第三个会话改回同一原种子，报告 `prior=0`。两块板的重复导出均为幂等，运行期间和释放 Flash 后请求分区清单均被拒绝。最终六个会话停止，Flash 已释放，活动租约为零。

逐份回核六个证据 ZIP、来宾标记和 16 MiB Flash。每份导出指向 ZIP 中对应分区的实际字节。分区外字节均与各自基础镜像一致，且两板首次导出和再写回后的分区 SHA-256 分别一致。离线汇编对照使用既有 ESP32-S3 的 ESP-IDF 5.5.4 与 6.1.1 构建，均重现旧版 Flash 与种子的字节，未增加 S3 来宾运行。范围为固定探针的原生 LittleFS，SPIFFS、浏览器、完整固件审核和实体 Flash 为 `NOT RUN`。 [六会话凭据](evidence/core2-nesso-littlefs-summary.redacted.json)

## Core2 受控 HTTP

精确 `m5core2`、`qemu-wifi` 和 `core2-openmac` 组合在 Linux ARM64 的私有网络命名空间中运行。HTTP 夹具需要显式启用。网络为开放式 STA，外层容器无网络，隔离采用入站与出站默认拒绝。夹具仅使用隐式本地端点，宿主无外部路由。Board 能力和 worker 命名空间能力分别检查。

同一探针的允许 Host 运行取得 HTTP 200，最终 TCP 捕获中的响应正文与期望 SHA-256 一致。来宾独立输出 `http=1 dns_a=1 dns_nxdomain=1 udp=1`。拒绝 Host 运行取得 HTTP 403，捕获不含预期正文，来宾输出 `http=0 dns_a=1 dns_nxdomain=1 udp=1`。两次均完成一次 DHCPv4 DORA，保留一条双向 TCP 和三条双向 UDP 负载流。Reviewer 的实际执行规划、准入和终态数据面收集链路在允许组返回 `OBSERVED`。完整审核队列和整单结论为 `NOT RUN`。

缺少命名空间的对照在分配租约前返回 HTTP 503 与 `network_isolation_unavailable`。有来宾运行的两条测试均收集证据后停止，释放 Flash 且活动租约为零。原版 Core2 应用、TLS、WPA2、IPv6、实体射频和浏览器为 `NOT RUN`。 [HTTP 与隔离对照](evidence/core2-contained-http-summary.redacted.json)

## Dial 原版快速旋钮

两次冷启动使用同一 vinylM5Dial 1.0 R1F30 和只读 GPIO 观察版原生运行时。每次用同一轨道种子作默认 35 ms 和快速 5 ms 每边沿输入。曲目结果由 Port B UART 独立回读。两次合计默认组匹配 18/18，快速组为 15/18，快速组的 12 次满圈匹配 9 次，6 次短输入全部匹配。

模型正确送达预期 Gray 边沿。观察到的 17,263 对来宾编码器 MMIO 读取中，没有一对横跨实际边沿。快速组有九个相位未被两路读取采到。三个漏档样本均为 16 格输入，使用来宾实际读取重算的计数为正负 60 而非完整的正负 64，预测曲目与实际 UART 一致。该归因限这三次原版快转样本。快转边沿实测间隔为 5.030–10.681 ms，公称 5 ms。未验证实机旋钮、其他运行时或更大输入样本。 [Dial 两次冷启与逐手势摘要](evidence/dial-fast-original-readback-summary.redacted.json)

## Tab5 原版启动与 DSI 帧

相同 98TAB5 原版分别在 0.50.0 和 1.1.0 GT911/ILI9881C 运行时普通启动。两个 60 秒目标窗口都没有施加输入、连接调试器或写入来宾内存。0.50.0 收到一个 boot banner、零 `SW_CPU_RESET`，运行中的 29 次帧获取均要求匹配 ELF。1.1.0 收到 32 个 boot banner 和 31 个 `SW_CPU_RESET`，运行中的 29 次查询均看到 DSI 已连接但没有完整帧。两条运行的初次查询各早于会话就绪。

同一 1.1.0 板型设置的独立原版 CarPlay 仅作显示正控。运行中的 14 次帧查询均返回有效 720×1280 PNG，首帧 2.003 秒。该正控覆盖显示启动，CarPlay 手机配对未测试。两种后端的版本、板级配置和帧获取路径同时不同，复位原因与 DSI 无帧原因仍待定位。原版 98TAB5 的应用分区是 OTA `app0`，未提供匹配 ELF。首个观察器尝试因启动时尚无 Flash 元数据报错，该次没有评估固件。后三个有效会话均停止、释放 Flash 且租约为零。 [Tab5 三次有效启动及观察器失败](evidence/tab5-stock-frame-summary.redacted.json)


## 源码与校验

模拟器主线为 `5f8e2f8fe97d2d76553efdf03068a8c3dcf83727`。完整本地平台套件在集成运行时源码上执行 2,396 项，跳过 10 项，其余通过。后续只更新文档与复验证据，51 项文档检查以及快照、运行覆盖、目录、配置、API 清单和变更范围检查通过。Reviewer 主线 `4537ea202bb51b0082fecb6c7cc271356d51aa8d` 的本地 197 项通过。变更可分别通过撤销模拟器和 Reviewer 的对应提交回滚。未提交 Burner。 [模拟器主线](https://github.com/m5agent/m5stack-esp-emulator/commit/5f8e2f8fe97d2d76553efdf03068a8c3dcf83727)
