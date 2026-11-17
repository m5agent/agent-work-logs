# 2026-11-18 原生固件后续复验

联合运行的基线为 `bd1dca3c74f8b9c2654e1ba3590e1f282d2071b0`，冻结 Xtensa QEMU SHA-256 为 `44d5b221e506c6b85dcc5d46d9d97a202eb6eca0a5713108a95f35676aed50f5`。本轮在独立 Device Service 会话对四组固件场景和一组 S3 崩溃控制固件进行 virtual-device validation。下列源码与二进制身份各自对应实际执行的对照和候选。总体为 `PARTIAL`。

| 范围 | 结果 | 复验 |
| --- | --- | --- |
| Cardputer ADV #234 原镜像、候选准入、审核与官方对照 | PASS | 基线来宾 Flash probe 失败，修复后组合和导入各返回 409，审核为 `E_STATIC`，官方 8 MiB 正控启动出画。 |
| Dial 原版 5 ms 旋钮 | PARTIAL | 冻结构建复跑 46/46，诊断再次看到 GPIO 相位完整但应用漏读整段相位。 |
| Cardputer ADV S3 CRC32 和 SHA256 | PASS | 两个受控 UART 崩溃各读出五个匹配 ELF 的任务上下文，诊断可在停止后回读。 |
| NC1020 原版画面 | PASS | 独立 K132 候选中，追踪和无追踪运行均得到完整合成图案，继续验证冷导入与 G0。 |
| StickS3 配网后 Flash 新会话启动 | PASS | 相同配置后 Flash 的旧版只见 DISCOVER。修复后启动直接走 STA，完成 DORA 和 ARP。 |

## Cardputer ADV #234 容量错误

2,041,968 字节的原版合并 BIN SHA-256 为 `53d73494dc80c8ff3e6ae8a7a8a28b4130f0d2cfe6907f1fa569531932209826`。虽然镜像文件短于 8 MiB，结构有效的 bootloader 头与分区表声明的实际容量均为 16 MiB。旧版准入返回 HTTP 201，补齐到 8 MiB 后运行同一 BIN。原版来宾输出 Flash probe 容量错误和 `ESP_ERR_FLASH_NOT_INITIALISED`。

候选源码 `6c28cbb59641d02b0dcdc892488e6868bc4b0ea9` 让合并和包导入两条路由都返回 HTTP 409 `firmware_flash_contract_mismatch`，保留 8 MiB 和 16 MiB 的结构化字段。保存快照的实际审核进程给出 `E_STATIC` 和容量诊断，未分配来宾会话。初版观察脚本两次在读取不适用的审核字段时失败。独立复验用实际保存的报告核对错误码。相同 QEMU 和候选服务运行官方 Cardputer ADV 8 MiB UIFlow2，取得 240×135 非黑画面。此结果覆盖所测准入和应用启动路径。物理烧录为 `NOT RUN`。[#234](https://github.com/m5agent/m5stack-esp-emulator/issues/234) · [摘要](evidence/cardputer-adv-flash-capacity-summary.json)

## Dial R1F30 快速旋转

此前同原版原生运行，反向 16 格、5 ms 从第 2 轨选至第 1 轨，预期第 7 轨。三次新冷会话在完全相同的冻结 QEMU 和原版 BIN 上为 46/46，含 14 次快速整圈。既有偶发失败仍保留。

四次带 USB 观察的诊断在 35 ms 条件为 36/36。5 ms 下正向整圈 6/12、反向整圈 7/12、短动作 11/12。重现第 2 轨到第 1 轨时，64 个 GPIO41/40 相位顺序正确，相邻间隔 5.041–8.217 ms，期间第 2、47 个相位的整个窗口均没有 GPIO_IN1 读。来宾的 GP-N9301 索引播放命令确认了实际选择。另一次应用串口的 click batch 直接报告了 −15。单独关闭 USB 捕获后仍出现一次短反转漏读，18 个动作共 17 次准确。

证据把所测分歧定位到原版对 GPIO 的轮询窗口。诊断本身的日志开销可能影响时间，所测诊断频率无法作为冻结运行时或真机的故障率。一次诊断缺少可选图像解码依赖，保留记录的轨迹及串口，当次没有证据 ZIP。后续采集保留成功的 ZIP。默认节奏为 35 ms，显式 5 ms 原版路径仍为 `PARTIAL`。[测试计数和包校验](evidence/dial-run-integrity-summary.json) · [诊断时间线](evidence/dial-diagnostic-timeline-summary.json)

## Cardputer ADV S3 UART 崩溃任务

候选 `bf47364af19bbc3d93e35e38d86f58e739744d51` 对普通原生 QEMU 的 ESP32-S3 UART 转储添加解析。使用两份实际运行的 Cardputer ADV 控制固件分别触发 CRC32 和 SHA256 格式。基线串口已报告传输完成，但服务状态停在 `uart_reported_complete`。候选在同一冻结 QEMU 上核对接收到的 8,912 和 8,940 字节转储，各读出五个任务上下文。匹配 ELF 时识别崩溃任务 `fixture_fault`，优先级和基础优先级均为 2，TCB 栈使用 512 字节、剩余 3,580 字节。无 ELF 或错配 ELF 时只提供上下文。

API、同会话 ZIP 和离线解析一致。同一候选重启隔离服务后仍可回读诊断。Core2 原生匹配 ELF 控制同时通过。此前 StickS3 `qemu-wifi` 的只读 watchdog 记录没有观测到转储，也没有上传 ELF。该样本和其它 S3 板为 `NOT RUN`。[固件、运行时和包校验](evidence/s3-coredump-summary.redacted.json)

## NC1020 原版画面与 K132 ST7789

源码候选 `a7cf9c08970f8f1c487efab86965c2c019be9982` 仅调整 K132 板的 ST7789 地址顺序。原生 GRAM 为 240×320，偏移 52、40，沿 `MADCTL` 应用来宾地址顺序，并按横向安装角度扫描输出。原版 BIN 和 64 MiB FAT16、16 KiB 簇的合成介质保持一致。冻结 QEMU 证实原版冷启动能取出 ROM/NOR、运行并 G0 保存，持续帧只能匹配裁剪路径。候选运行时 SHA-256 为 `14ed4ae1ed1819f7cc03cf116e491ce163519b5f1182db02615649385d499fd4`。

无追踪候选在来宾 26,070 ms 返回载入，26,319 ms 心跳，26,423 ms 出现首次完成 LCD 绘制的阶段标记。G0 前两张和操作后同一 240×135 帧均为完整合成图案，fit 1.0、SHA-256 一致。实际 guest 写入的 206 个 ROM bank 和 512 KiB NOR 保持字节匹配，G0 留下 99,384 字节。画面启动阶段仍有原版固件的黑色填充。控制探针核对 32,400 个屏幕像素，并通过存储和 idle RX 检查。K132 Factory v0.08、v0.09 和 UIFlow2 v2.5.4 在无追踪条件均取得画面与输入响应。源码范围和应用验收限于这些测试。[逐轮帧与画面状态](evidence/nc1020-native-geometry-summary.redacted.json)

## StickS3 配网后 Flash 新会话

基线 StickS3 原版 v0.2.4 正常提交配置并从运行中的同一来宾导出 Flash，SHA-256 为 `944dd200046b6976a430136ef613292ea45edfd5ecf3895eb4e3eac9ebcee2cb`。就独立导入路径，旧隔离对端仍等待 AP 侧流程。新会话的 pcap 只看到 32 个 DISCOVER，涉及两个客户端。基线终态 `PARTIAL`。

候选 `287b94ca036d64baca54cb370bf471c289125352` 根据虚拟链路上实际 DHCP 流量识别已配置来宾。保持同一 QEMU，从基线读取 SHA 完全一致的配置后 Flash 作为输入，关闭旧会话后建立新 lease。新会话的第 1 代报告 `station_on_start=true`，独立 pcap 确认 1 次完整 DORA、ACK 后的来宾 ARP，应答状态为 `PASS`，没有再次提交门户。应用区仍与作者原始发布相同，NVS 已配置。候选执行另外生成一份不同的配置后 Flash，两个哈希保留在摘要中；最终同字节对照使用基线保存的镜像。该结论覆盖原生隔离 IPv4 链路与配置后新会话，受保护热点和云功能为 `NOT RUN`。[导入和 pcap 审核](evidence/sticks3-new-lease-summary.redacted.json)

## 复现入口和边界

在各候选源身份下运行独立 Device Service，验证运行时与固件 SHA。#234 对照使用合并编排和包导入 API，普通设备的原版运行走独立会话。Dial 使用普通 `/input` API 下的有符号 encoder 动作，以 GPIO 相位及来宾 UART 校验选曲；NC1020 用 `storage` 附加相同介质，以串口、面板状态和帧核对。S3 探针见源码 `tests/firmware/crash_diagnostics`，比较 `/crash`、证据 ZIP 与离线结果。StickS3 首轮申请普通原生配网会话、导出已配置 Flash、保留证据并停止，再经固件合并接口和 `sticks3-open-softap-provisioning` 申请独立新 lease。

会话证据 ZIP 在停止前采集，对照及候选可按各自源码和运行时哈希复跑。真机、物理射频、浏览器 WASM 和音频声学为 `NOT RUN`。[机器可读结果](run.json) · [证据索引](evidence/README.md)

## 最终整合复验

使用固件路径一致的隔离 Device Service 执行源码 `25b2e2069044c607c93192d7be691a91c877fdc9`、QEMU `14ed4ae1ed1819f7cc03cf116e491ce163519b5f1182db02615649385d499fd4`，审核源码 `812e59dec72308b2e063366a7e751c0564dbb73e`。随后只调整文档索引、当前能力表述和 Markdown API 版本，发布提交 `8c65905e466c69a62239371f1fcd254c183b0712` 的 `platform/`、`patches/`、`scripts/` 和 `tests/` 字节与执行提交相同。169 层 QEMU 补丁正向和逆向应用通过，逆向回到固定上游，10,450 个源码和文件模式逐项匹配。[编译输入摘要](evidence/combined-native-stack-summary.json)

- #234 原版 `/firmware`、`/firmware/import` 和存量固件记录的 `/sessions` 都在分配来宾前拒绝。实际保存快照的审核终态为 `E_STATIC`，Chromium 中“静态分析详情”显示 Flash 容量及双方十六进制字节数。8 MiB 官方正对照正常出帧，释放租约。[整合结果](evidence/combined-flash-capacity-summary.json)
- 同一 StickS3 已配置 Flash 再次通过新 lease 的实际 DORA 和 ACK 后的来宾 ARP，没有门户表单。同一会话两次重置的独立运行也通过，三代 pcap 分别含 2、1、1 个完整 DORA，全程只提交初次配置一次。[导入证据](evidence/combined-sticks3-cold-summary.json) · [复位证据](evidence/combined-sticks3-reset-summary.json)
- Cardputer ADV 两种 UART 转储均再次与官方离线工具的五个任务详情一致，同会话证据和服务重启后可读。[整合崩溃证据](evidence/combined-s3-crash-summary.json)
- NC1020 两次无追踪整合运行均读回完整 ROM/NOR、正常写出 G0 且无 watchdog，图案分别停在部分区域和左侧单条像素，未出现完整 LCD 绘制完成标记。用同一二进制开启现有显示事务追踪后获得 G0 前后完整图案。追踪会改变观测时序，稳定出帧保留 `PARTIAL`。三份原厂正对照通过，所有会话均清理。[无追踪整合结果](evidence/combined-25b2-panel-summary.json) · [追踪对照](evidence/combined-25b2-traced-panel-summary.json)

发布源码本地平台测试 2379 项，跳过 10 项，其余通过。审核端 Python 3.9 的 183 项及 34 项 Node 契约通过。浏览器 Node 契约不包含已部署 WASM 的来宾验证。[发布校验](evidence/release-gates-summary.json)
