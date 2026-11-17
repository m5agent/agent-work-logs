# 原生固件审核后续验证报告

日期 `2026-11-17`。验收路径为 virtual-device validation。源码组合 `cccc83b95d4c89f043d6d6d77d21161bc5ece106` 收录这些验证。各独立执行的代码基线、固件/规范化 Flash、运行时及留存 ZIP 的 SHA-256 在对应摘要中，组合源码标识不改变实际试验身份。

## 运行诊断与 Tab5

先在原生 Nesso N1 启动已知 MWDT 探针，调用 `GET /api/v1/sessions/{id}/crash/cpu-pc`。QMP 核对 `esp32c6-machine`、`espressif-riscv-cpu` 和 `riscv32` 单核。隔离夹具暂停时两次读数一致，恢复后运行状态确认。原 abort 探针的当前 PC 为 `0x40800412`，同会话 guest MEPC 为 `0x40804cb8`，匹配 ELF 解析为 `panic_abort`。原版 RFID 固件在打印 ROM 标记后完成当前 PC 读取，RFID 业务未执行。Core2 的两核控制保留相同暂停和实际 CPU1 watchdog 证据。测试结束后均完成证据 ZIP 与资源释放。[执行摘要](evidence/c6-live-pc-summary.json)

Tab5 原版 Arduventure 在 ST7123 板型用触摸按下与释放报告产生界面和状态变化。空白区域对照不改变帧，速度控件从 1× 切换到 2×，游戏内四次触点移动光标后回到 `(0,0)`。单独客体在边角及中心记录触点、释放和无输入无 IRQ 条件。另一原版 CarPlay 在同一个 worker 选择 GT911，拖动产生 24 个已确认报告，独立点击打开弹窗。Arduventure 通用 saved-snapshot 审核首帧和 60 秒观察通过，仅一项泛化输入被接受且画面未变化，结论仍为 `manual_review / E_INTERACTION_INPUT_UNSUPPORTED`。ST7123 连续滑动、USB 和物理触控未验证。[执行摘要](evidence/tab5-st7123-touch-summary.json)

安排明确屏幕触点的独立复审使用 `f4d0e690dfef178e2f022cc556ac44e5af92bcaa`。9 项均获接受并产生指定变化，观察 `60.3889` 秒。长按声明 `touch_hold_center` 保留未运行，整体仍为 `SIM_PARTIAL / E_INTERACTION_INPUT_UNSUPPORTED`。[明确触点复审](evidence/tab5-explicit-review-summary.json)

## NC1020 原版持久化与 Dial UART

NC1020 使用原镜像内置数据和无替换 ROM/NOR 的外接卡。通过虚拟 BOOT 按键触发保存，客体串口出现 `state save /sd/nc1020.state: ok`，记录 213 次 SPI 单块写。导出的卡镜像交给新会话后读取固定状态并恢复心跳。存档和读回通过，载入后出现黑帧。审核侧复跑用同一会话的有界 UART 事件断言明确验证存档，整体仍为 `manual_review / E_INTERACTION_CLAIM_PARTIAL`。[存档、审核和冷导入摘要](evidence/nc1020-save-summary.json)

另以自制 ROM/NOR 文件测试冷导入。64 MiB FAT32、512 字节簇在 60 分钟围栏内到 128 bank。64 MiB FAT16、16 KiB 簇首轮在 `591944` guest 毫秒到 96 bank，随后触发 CPU1 interrupt watchdog 和软件复位。冷导入保持 `PARTIAL`。另外，两次追踪场景均在各自 540 秒和 1800 秒观察时限内完成清场，并都记录 CPU1 中断 watchdog 与软件复位。未追踪的旧 FAT32 对照达到 128/206 bank，记录任务 watchdog 警告而无中断 panic。几何、运行条件和源码身份分别保存。[冷导入对照](evidence/nc1020-cold-controls-summary.json)

Dial N9301 的两组原驱动试验分别在 PORT A/B 通过七轨索引、控制事务和坏帧拒绝。无介质对照索引为零。原版在 PORT B 实际发出两次播放命令，GPIO 边沿和 UART 记录分别支持曲目 4 与 2。原版画面保持黑帧，声音输出及物理介质未运行，原版功能保持 `SIM_PARTIAL`。[执行摘要](evidence/dial-audioplayer-summary.json)

## 只读预检与原版 ADV 对照

`GET /api/v1/devices/{device_id}/capabilities` 在独立实例中分别验证了本地后端就绪、二进制缺失、当前二进制不含要求的机器、已登记但禁用的设备、未知型号以及无有效授权。每次读取后的活动租约和新增会话均为零。`case_registered` 仅说明目录含该板的控制器用例，`not_tested` 表示该目录当时无相同板型与组件的登记。Tab5 的独立原版与客体控制器新证据在前节单独给出。

设备能力预检报告 `m5cardputeradv` 的 SPI SD 路径可用后，使用同服务上传原版 Cardputer ADV MP3 Player v1.0.0 和匹配 FAT32 夹具。文件列表取证后按 Return，CMD17 计数从 4 增到 66。数字 PCM 中 50,780 个非零样本和 11 段音调窗口匹配夹具。应用程序区字节保持原样。停止前留存 ZIP，之后释放 Flash 和租约。[执行摘要](evidence/device-capabilities-summary.json)

精确组合 `3e1084e717ac9514142c356593d3f91f30c4b3b3` 隔离复跑能力接口、Dial 原版 UART 及 ADV 原版 MP3。ADV 输出 53,084 个非零 PCM 样本和 12 段匹配音调窗口。Dial 两次旋转仍产生曲目 4 与 2 的 UART 命令，两项会话均完成清场。[组合复验](evidence/integrated-3e-native-summary.json)

## 精确组合复审

`cccc83b95d4c89f043d6d6d77d21161bc5ece106` 与审核器 `7e1ac6801ee3e505e334253ac506c67f16ece8b0` 分别通过本地平台 2,339 项检查（跳过 10 项）及审核器 153 项检查。随后以该组合对三份保存快照进行隔离复审。NC1020 同一会话串口存档事件及 99,384 字节输出通过，完整结果仍为 `E_INTERACTION_CLAIM_PARTIAL`。Dial PORT B 的原版 N9301 UART 控制通过，画面仍触发 `E_NO_FRAME`。Arduventure 的九个明确动作及 60 秒观察通过，屏幕长按声明仍触发 `E_INTERACTION_INPUT_UNSUPPORTED`。三项均保留局部功能证据和人工复核结论。[最终复审摘要](evidence/integrated-final-review-summary.json)

## 复现入口

- C6 探针、匹配 ELF 与真实 QMP 采样。[C6 测试说明](https://github.com/m5agent/m5stack-esp-emulator/blob/cccc83b95d4c89f043d6d6d77d21161bc5ece106/tests/firmware/crash_diagnostics/riscv_c6/README.md)
- Tab5 板型选择、原版定点触摸和独立控制器读取。[Tab5 测试说明](https://github.com/m5agent/m5stack-esp-emulator/blob/cccc83b95d4c89f043d6d6d77d21161bc5ece106/docs/evidence/2026-11-17-tab5-st7123-touch/README.md)
- 原版 NC1020 的文件系统和 SD 证据。[SPI SD 回归说明](https://github.com/m5agent/m5stack-esp-emulator/blob/cccc83b95d4c89f043d6d6d77d21161bc5ece106/tests/firmware/spi_sd_media/README.md)
- Dial 原驱动和同一原版 UART 控制。[Dial 测试说明](https://github.com/m5agent/m5stack-esp-emulator/blob/cccc83b95d4c89f043d6d6d77d21161bc5ece106/docs/evidence/2026-11-17-dial-audioplayer/README.md)
- 隔离服务预检、鉴权、只读清场及 ADV guest 对照。[设备 API 测试说明](https://github.com/m5agent/m5stack-esp-emulator/blob/cccc83b95d4c89f043d6d6d77d21161bc5ece106/tests/uiflow2/api_sweep/README-device-api.md)

## 交付边界

所有试验为隔离虚拟设备运行。原始固件、ZIP、进程标识和私有控制信息未纳入公开记录。未验证任何物理、浏览器 WASM 或未列固件的行为。本记录不申请发布到 Burner。若需要撤回单项代码，可按组合源码中的独立提交回退并重跑相应受影响会话。
