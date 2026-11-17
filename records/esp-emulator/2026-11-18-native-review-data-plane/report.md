# 原生固件审核数据面补齐

## 目标和修改

在应用原始字节保持一致的前提下，为原版审核提供同来宾的网络、存储和交互证据。使用独立服务和会话私有的虚拟 Flash、SD 介质与 Unix socketpair。模拟器的正式原生 Xtensa 配方增加 0216、0217、0218，依次覆盖 GP-SPI 空闲读入 DMA、StickS3 门户到 STA 交接和 Dial 三线 GPIO 面板探测。Device Service API 版本为 1.71.0。QEMU 可执行文件 SHA-256 为 528ab418daedc9dab895fcebd4092b1a284563513c8ed7aca06b06527b58061a。

## 原版复验

- **StickS3-Claude-Codex-Assistant v0.2.4。** 旧运行时在正常 WiFiManager 表单得到 HTTP 200 后发送扫描请求，未关联。候选初测能发送关联请求和 DHCP Discover，但共存的 AP 和 STA 需要独立的 DMA 接收匹配。最终原版同会话抓包含两条 DHCP DORA、两条门户 HTTP 流以及 STA 在获配 IP 后的 ARP 回应。用带固定原版 SHA 和启动头的保存快照经审核器复跑，本地配网为 PASS，云端功能为 NOT RUN，整份审查保留 SIM_PARTIAL。只读门户控制同一原版映像，仍完成单条 DORA 与 GET 流。
- **CardputerDict 0.6.4。** 审核器过去先执行推断出的 Fn+W，打开 Wi-Fi 编辑器后，缓存快捷键到不了词典。现在显式 SD 断言优先于无关的推断快捷键。Fn+R 对照未写入，Fn+Shift+R 触发来宾真实 SD 文件写入。停止后读回同一会话的 68 字节 ecdict.cidx，原夹具和原版应用保持原始字节。完整复审的其他交互仍保留待核。
- **vinylM5Dial R1F30。** 旧模型遗漏 Dial 的 GPIO 面板探测通路，原版虽运行但未开始 SPI 显示事务。补真实三线板级接线后，原版输出 240×240 有效帧。默认 35 ms 正反整周、中心触控暂停/恢复、上下触控音量及物理按键的停止/播放都有原版 UART 命令对照。官方 UIFlow2 同运行时也输出画面。显式 5 ms 下的整周负向复测交付 64 条 GPIO 边沿，仍有一次漏选曲。
- **SPI/SD 和原版 MP3。** 选中 SD 的真实 DMA 读和非 DMA FIFO 在 A/B 都成立。片选为高时，基线不更新 DMA 缓冲区。候选将采样到的空闲 MISO 写回对应长度缓冲区。在合并运行时，Cardputer ADV MP3 Player v1.0.0 从测试 SD 卡读块后播放，CMD17 从 4 增至 66，PCM 有 12 段匹配 524 Hz。NC1020 原版首 bank 约 5.9 来宾秒，长跑只证明部分 ROM 已复制，整套 ROM/NOR 冷导入继续开放。

- **EMBER 2.1 回归。** 新的精确虚拟运行时及审核器在隔离环境用同一原版进行 60 秒复审，返回 SIM_VERIFIED，串口记录一次上电，无 watchdog 或复位。前一常驻环境的两次异常记录仍保留，本次覆盖的是隔离复验。

## 验证方法

在 Device Service 创建板型与固件 SHA 绑定的虚拟会话，保留声明输入、串口、真实外设响应、帧和证据 ZIP。网络在关闭前采集 ZIP，关闭后从同会话读最终 pcap 数据面。SD 动作核对同一会话的写入戳、前后截图和停止后 FAT。独立复现命令、构建配方及源码证据见 [StickS3](https://github.com/m5agent/m5stack-esp-emulator/tree/a0fa14ae26f047fe4bef2c53681f9ea61b13eb8e/docs/evidence/2026-11-17-sticks3-portal-station)、[Dial](https://github.com/m5agent/m5stack-esp-emulator/tree/a0fa14ae26f047fe4bef2c53681f9ea61b13eb8e/docs/evidence/2026-11-17-dial-gc9a01-gpio-probe)和 [SPI SD](https://github.com/m5agent/m5stack-esp-emulator/tree/a0fa14ae26f047fe4bef2c53681f9ea61b13eb8e/tests/firmware/spi_sd_media)。

原生运行时的提交与证据摘要分别固定，最后模拟器提交只同步 API 测试清单的合同版本。历史常驻运行保留为独立状态。清理时停止自己的会话、释放租约与可写 Flash。复现使用公开原版或自编探针，工作记录保留证据摘要、哈希和状态。

## 合并门禁

平台全量执行 2,367 项测试，跳过 10 项。审核端用常驻服务所用的解释器执行 182 项测试，全部通过。覆盖清单、外设目录、QEMU 档案、项目快照和 PR 范围校验通过。从固定上游 QEMU 正向应用 165 个补丁，155 个触及路径与构建源码一致，逆向回放还原基线。冻结包重新核对两套源码、原生运行时、启动上下文和 2,178 个网页资源。
