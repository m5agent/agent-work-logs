# 2026-11-18 原生虚拟设备联合复验

同一最终源码 `bd1dca3c74f8b9c2654e1ba3590e1f282d2071b0` 和同一 Xtensa QEMU 二进制 `44d5b221e506c6b85dcc5d46d9d97a202eb6eca0a5713108a95f35676aed50f5` 分别执行 StickS3 原版配网重置、Dial 原版和官方固件、NC1020 原版冷导入、Core2 两个受控崩溃。所有验收均为 virtual-device validation，总体为 `PARTIAL`。

| 路径 | 状态 | 在最终构建上的观察 |
| --- | --- | --- |
| StickS3 原版配网与恢复 | PASS | 配网页面与提交各发生一次。三代 pcap 捕获的 DORA 为 2、1、1。 |
| Dial 原版旋钮与控制 | PARTIAL | 旋钮 9/10 次准确选曲，六项控制 6/6。 |
| Dial 官方画面控制 | PASS | 240×240 帧含 57,509 个非黑像素，采集到 35,968 条 GP-SPI 传输。 |
| NC1020 冷导入与存档 | PASS | 观察到运行心跳，Flash 核对 206/206 ROM bank 和 512 KiB NOR，G0 触发并留下可核对的存档哈希。 |
| NC1020 画面 | PARTIAL | 该轮早期样本全黑，可采区域只覆盖目标画面的一部分。 |
| Core2 abort 和 watchdog | PASS | 两种受控崩溃分别读出 6 和 5 个任务上下文，匹配 ELF 的元数据可在停止后服务重启读回。 |

## StickS3 原版配网与重置

使用作者 v0.2.4 的原版应用，并按发布工程编排 Flash。冷启动进入首配流程，隔离对端完成页面 GET 和表单 POST。只有冷启动提交表单。调用同一会话的 guest reset 两次后，来宾在新的抓包区间作为站点重新完成 DHCP。每代的 station ACK 后能看到使用所得地址的 ARP 响应。三次 ROM 启动横幅与两次重置吻合，来宾应用分区保持原字节，配置写入 NVS 后跨本轮两次重置保留。

独立抓包读回将各代偏移核对到实际 pcap 数据包边界。最终执行未发现 station DHCP 事务 ID 跨重置复用。修复允许事务 ID 重用，以各代的新抓包区间判定新交换。较早版本曾在来宾转入 STA 后继续等待首配 AP lease，另一个候选曾错误要求 DHCP 事务 ID 唯一。本轮保留一张会话画面及各代取证 ZIP，最终抓包 SHA-256 与停止后读回一致。结论覆盖隔离对端、虚拟 IPv4 数据面和同一会话重置。物理射频、受保护热点、跨会话导入配置和云功能为 `NOT RUN`。[最终运行摘要](evidence/sticks3-rejoin-summary.redacted.json) · [作者发布](https://github.com/bulb888/StickS3-Claude-Codex-Assistant/releases/tag/v0.2.4)

## Dial 原版与官方对照

用原版 vinylM5Dial 1.0、PORT.B 的 AudioPlayer 和真实虚拟 GPIO 相序注入。十次有符号旋钮动作通过来宾的新 UART 索引播放帧和设备曲目验证。唯一未通过项为反向 16 格、5 ms，记录到 64 个 GPIO 边沿后，来宾发出了播放第 1 轨的命令，预期为第 7 轨。该轮原版结果为 `PARTIAL`。中心暂停和恢复、音量增减、按下停止和恢复均引发预期设备状态变化，六项均保留对应 UART 和帧指纹。

原版 240×240 帧有 57,600 个非黑像素。相同最终运行时的官方固件独立会话读到 57,509 个非黑像素和 35,968 次 GP-SPI 传输。官方固件的屏幕正控和原版 UART 控制只覆盖所测虚拟数据面，实际音频列为 `NOT RUN`。早先 0220 独立候选的 20/20 证据保留在其源码记录，最终合并重复的漏选归因尚待继续定位。[最终运行摘要](evidence/dial-summary.redacted.json)

## NC1020 原版冷导入与 G0 存档

通过 Device Service 导入原版 8 MiB 合并镜像，初始会话 Flash SHA-256 与原版相同，挂载已核对 SHA-256 的 64 MiB FAT16 SD 工件，簇大小 16 KiB。到心跳观察点耗时 26.884 秒，未观测到任务 watchdog。串口最大阶段标记为 192，随后导出的同客体 Flash 逐字节核对 206/206 个 bank，共 6,750,208 字节，并确认 512 KiB NOR 与本轮合成载荷一致。应用和 bootloader 保持原字节。该结果穿过卡挂载、文件读取和 guest 写 Flash 的实际路径。

同一运行客体注入 BOOT 按住 0.85 秒的 G0 保存动作。串口出现 G0 存档标记，停止后仍可核对存档 SHA-256。严格脚本的画面检查退出码为 1。早期帧全黑，可采的 16,200 像素子集只占目标 28,800 像素的 56.25%，因此视觉验收保持 `PARTIAL`。同构建的第二次冷导入在 26.229 秒到达心跳，仍为 206/206 和完整 NOR，保持零次任务 watchdog；G0 存档为 99,384 字节。第二次有连续两张相同的非黑裁剪帧，可见区域仍不足以完成完整几何验收。较早的冻结运行时在同一原版与 SD 上也完成冷导入，单次耗时 1,417.539 秒并出现 245 次任务 watchdog 警告。计时为各次宿主观测值。物理 SD 时序及真机画面为 `NOT RUN`。[冷启动、Flash 与输入摘要](evidence/nc1020-cold-summary.redacted.json)

## Core2 匹配 ELF 的崩溃任务

在两个独立的 Core2 会话运行明确触发 abort 和 watchdog 的控制固件，分别上传与实际固件匹配的 ELF 和不同构建的对照 ELF。实际串口生成的 ESP32 Xtensa ELF32 CRC32 core dump 在 API、同一会话的 ZIP 和独立离线解析中一致。abort 解析出 6 个任务，watchdog 解析出 5 个任务。两例的崩溃任务均为 `fixture_fault`，优先级和基础优先级为 2，基于保存的 TCB 栈边界解析为使用 1,696 字节、空闲 2,396 字节。原始 PC/SP 保留，不同构建的 ELF 不参与解析。停止与重启隔离服务后可重新读取同一诊断。范围仅覆盖这两份 Core2 控制固件，C6 任务元数据为 `NOT RUN`。[Core2 运行摘要](evidence/core2-coredump-summary.redacted.json)

## 构建与复现

从本文提交开始，用源码的 `scripts/bootstrap-unit-runtime.py` 应用原生补丁链，验证运行时二进制哈希。集成点包括 0219 的 StickS3 重置后站点复连、0220 的 Dial 旋钮纳秒截止时间、匹配 ELF 的 FreeRTOS 任务元数据，以及 0221 按 GPIO Matrix 或 IO_MUX 选择 Cardputer GP-SPI 设备时钟路线。独立原生 Device Service 是这四条测试的共同入口。

1. 按各摘要登记的板型和哈希绑定固件，并用独立工作状态启动 Device Service。通过 `/api/v1/artifacts`、`/api/v1/firmware` 或 `/api/v1/firmware/import` 准备镜像，再申请原生会话。
2. StickS3 使用 `sticks3-open-softap-provisioning`，同一 lease 的 `/reset` 执行两次，按 `capture_start_offset` 验证 DORA 与 ARP。Dial 使用 `kind=encoder`、所列 `delta` 和 `edge_period_ms`，对照 GPIO 边沿、播放轨道和来宾 UART。
3. NC1020 附加摘要所列 SD 工件，读取冷导入后的 Flash 核对合成载荷，并通过同会话 BOOT 长按采集 G0 存档结果。Core2 使用仓库 `tests/firmware/crash_diagnostics` 的对应探针，比较 `/crash`、ZIP 和离线解析。
4. 在停止前请求各自证据 ZIP，停止时保留会话历史并按各实验需要释放可写 Flash。最后回读状态和 lease。

联合平台套件执行 2,374 项，2,366 通过、8 项跳过。审核端 Python 3.9 套件 182 项全部通过。运行时覆盖、外设目录、QEMU profiles 与项目快照四项生成校验、Node contracts 及 scope 均通过。独立补丁链审核核对 168 层正向应用和 168 层反向还原，固定上游工作树干净，10,450 个跟踪输入逐项匹配。首次隔离审核进程在启动健康检查阶段超时。独立复跑用相同最终运行时完成 StickS3 原版快照复审，本地 AP 范围为 PASS，云功能仍为 PARTIAL，会话释放后 lease 为零。公开附件仅保留脱敏证据及私有件的字节数、SHA-256。所有本轮测试会话均完成清理。物理硬件、浏览器 WASM、公开部署和 Burner 提交不属于本记录的验收范围。[回归摘要](evidence/platform-regression-summary.json)
