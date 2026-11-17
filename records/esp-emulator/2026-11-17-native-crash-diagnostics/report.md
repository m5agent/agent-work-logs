# 原生崩溃证据与原版固件复审

## 背景和改动

原有审核按串口关键字判断崩溃。Tab5 重启后读到的核转储校验失败可能被误当作本次应用崩溃，符号和后台日志也缺少结构化的证据入口。

Device Service 在 `GET /api/v1/sessions/{id}/crash` 返回绑定会话、固件、设备和运行方式的诊断，并可将副本随 evidence ZIP 导出。记录分别描述主要 panic、看门狗、复位、串口核转储标记和模拟器 stderr。审核继续支持旧服务的串口回退，只有独立的 panic 标记或反复 CPU 复位才改变相关判定。

审核只在请求的 ELF artifact、完整应用 ELF 哈希和实际 panic 报告的前缀一致时接受函数名。核转储首尾标记可证明串口传输完成。核转储内部 CRC、任务状态与源码行级追踪未解析。

## Core2 受控复现

原生 Xtensa QEMU SHA-256 为 `cbc0ea74c5763a9d989562b7061516fb3489fdc4056ddce4e016d555c1b86bb2`。使用 ESP-IDF v5.5.4 `735507283d5b2f9fb363a1901172dbd9e847945d`，在 Emulator 源码 `3c65a511b9fdb74fa1906322447a1e5b146e302f` 的 `tests/firmware/crash_diagnostics/` 构建受控样例。Device Service 实际执行源码为 `271524908363e8666148a7b60932fcaf01b5d5ff`，两者平台实现一致。仓库和构建依赖见 [ESP Emulator](https://github.com/m5agent/m5stack-esp-emulator) 和 [固定 ESP-IDF commit](https://github.com/espressif/esp-idf/commit/735507283d5b2f9fb363a1901172dbd9e847945d)。

在样例目录用 `idf.py build` 构建 abort 版。用独立构建目录和 SDK 配置，以 `-DCRASH_PROBE_WATCHDOG=ON` 构建看门狗对照。按生成的 `flash_args` 合并成 16 MiB 镜像。分别保留 ELF 并上传两个 artifact。创建原生 Core2 会话，等待真实串口中的 `CRASH_PROBE_ARMED cpu=1` 和 `CORE DUMP END`。分别取无 ELF、匹配 ELF、交叉 ELF 的诊断，结束前请求含串口和诊断的 ZIP，随后停止会话并释放 Flash 和租约。保留一个已停止的看门狗会话，在隔离服务重启后重复读取。

| 对照 | 结果 | 观测 |
| --- | --- | --- |
| Core2 abort | `PASS` | Core 1 报告调用点 `0x400d7d17` 与回溯。匹配 ELF 的 5 个地址全部解析，其中包含 `trigger_fault`。 |
| Core2 CPU1 中断看门狗 | `PASS` | 串口报告 CPU1 中断看门狗，保留 CPU0 和 CPU1 寄存器 PC。匹配 ELF 的 13 个地址有 9 个解析，ROM 等地址保持原值。 |
| 错误 ELF 和保留会话 | `PASS` | 用另一构建的 ELF 无法通过身份核验。隔离服务重启后仍能读取匹配 ELF 的诊断。 |

受控固件和 ELF 的完整 SHA-256、PC 和原始 ZIP 哈希见 [Core2 受控证据](evidence/core2-controlled-crash-summary.json)。故障由固件样例有意触发，用于验证证据通路。

## 三份原版隔离复审

通过审核服务的保存快照入口，以 `sourceMode=saved_snapshot` 和 `useAgentReview=false` 创建 dry-run。创建前检查原版文件长度和完整 SHA-256，完成后重查报告、会话、ZIP 和租约。StickS3 使用同一 Xtensa QEMU，测试启动器启用受限 SLIRP、关闭 IPv6 并拒绝转发。Tab5 运行固定的 esp-emu 0.50.0，SHA-256 为 `a4c3468a4abf3f2e55ca0912fa7cdfbe5e101ecb6ab74a9ec35182d70ba6a771`。

| 原版 | 实际观测 | 审核结论 |
| --- | --- | --- |
| All day watch 0.3.8 | 60.022 秒串口与画面；A 双击送达但未见预期响应，B 按住 2 秒产生画面变化。此次诊断无主要 panic。 | `E_INTERACTION_CLAIM_PARTIAL`。 |
| M5TabOS 0.9.1 | 一次上电和六次软件 CPU 复位。串口报告核转储分区校验失败。esp-emu 在两个 hart 分别记录非法指令 `0x00000000`，PC 同为 `0x4ff10f12`；串口没有主要 panic。 | `E_SIM_MODEL_GAP`，归因未定位。 |
| 98TAB5 1.3.0 | 最新保存的原版完成 60.008 秒仅串口观察，一次上电，未观察到 panic 或连续复位。截图接口要求匹配 ELF。 | `E_EVIDENCE_UNAVAILABLE`，画面和触摸未验证。 |

历史的同哈希 All day watch 曾在 15.364 秒观察中报告 Core 1 中断看门狗和七个回溯地址。本次使用了较新的运行时和语义输入，未复现该故障，根因仍开放。M5TabOS 的非法指令与复位尚无足够证据支持固件或模型归因。两个更早的同版本 98TAB5 记录具有独立的 BIN 和 ELF 哈希。

三份原版均没有可用的精确匹配 ELF。在已保存的任务和内容寻址产物中均未找到这些完整哈希。两份 Tab5 声明的公开源码在检查时也没有发布包，默认文件树中没有 ELF 或 MAP。 [M5TabOS 发布页](https://github.com/cparadaa/M5TabOS-sistema/releases) [98TAB5 发布页](https://github.com/mochimochi-man/98TAB5/releases)

## 证据核验和边界

归档复查以只读方式解压六份现存 ZIP，校验 ZIP CRC，用诊断中 offset 和长度在原始串口字节上核对 SHA-256，并将诊断和 ZIP manifest 中的会话与固件身份逐项比对。审核侧串口摘要按统一换行的 UTF-8 文本计算，独立于 Device Service ZIP 原始串口字节。公开记录保留哈希、字节数和观测字段，省略原始 ZIP、串口正文、会话标识和执行路径。 [归档完整性摘要](evidence/archive-integrity-summary.json)

审核侧在 Python 3.13 和系统 Python 各通过 140 项测试。受控 Core2 诊断为 `PASS`，三份原版的功能和归因仍为 `PARTIAL`。物理硬件、浏览器与生产切换为 `NOT RUN`。所有隔离会话已经清理，未提交 Burner。此轮未修改常驻服务；后续若需回滚诊断消费者，可以恢复此前审核版本，同时继续使用原有历史和证据文件。
