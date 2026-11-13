# ESP Emulator 社区固件问题修复与复测报告

## 背景与范围

公开 [#216](https://github.com/m5agent/m5stack-esp-emulator/issues/216) 至 [#224](https://github.com/m5agent/m5stack-esp-emulator/issues/224) 报告了 C6 启动、PaperColor 宿主崩溃/USB/关机、AtomS3 黑屏、经典 Atom 看门狗、Core2 黑屏、StackChan 栈破坏及 eFuse 身份问题。本轮要求沿原版固件和真实控制器路径复现、修复和保留失败证据，不提交 Burner。

本报告最终源码快照固定为 [`98287067eaf558576d1120f213d676630d66c2bd`](https://github.com/m5agent/m5stack-esp-emulator/commit/98287067eaf558576d1120f213d676630d66c2bd)，基线为 `676ae67c67941b976be799782ef4af40827b666d`；后续摘要分别记录其固定源码与运行时身份。最终精确提交的平台套件结果尚未完成。本次归档补充尚未提交或推送。

## 根因、改动与实际结果

### #217：共享 IOMMU 的异核 TLB flush

共享 S3 cache IOMMU 在修改映射的 CPU 上通知所有订阅者，旧实现直接清理另一个正在执行的 vCPU 的软件 TLB，可与 atomic lookup 竞争。0182 将异核失效排入目标 vCPU 的工作队列，保留本核/启动前同步处理和 atomic 检查。

同一双核探针旧运行时 3/3 宿主失败，修复后 2/2 完成 200,000 次重映射。原 PaperColor factory 两轮 120 秒宿主存活；首次整合运行时再观察 300.74 秒无宿主退出，但记录 1 次 guest 断言及 2 次 `Rebooting`。结论仅限宿主崩溃修复，应用仍 `PARTIAL`。

证据：[cache/atomic 控制](evidence/issue217-cache-atomic-summary.json)、[整合复测](evidence/integration-summary.json)。源码：[0182](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/patches/qemu-m5stack-peripherals/0182-tcg-iommu-vcpu-flush.patch)、[可运行探针](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/tests/firmware/s3_cache_atomic/README.md)。

### #218：主动关机与故障终态分离

服务同时读取 QMP `SHUTDOWN` 的 guest/reason 和 `query-status=shutdown`，使用 `-no-shutdown` 留出末帧采集窗口，再走已有进程和 lease 清理。退出码、日志文字、白屏都不是关机原因的替代证据。

原 PaperColor/PaperDIY BIN 在故意缺失的 ready marker 条件下均以 `stopped/guest_poweroff` 收口，末帧可读。批量 runner 返回 `PARTIAL/guest_poweroff`、`application_ready=false`。PaperDIY 首次短窗未观察到关机的结果保留，默认时间线另行复测。

证据：[关机摘要](evidence/issue218-poweroff-summary.json)、[整合复测](evidence/integration-summary.json)。复现入口：[Device Service](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/platform/tools/device_service.py)：原始 artifact → merged firmware → qemu session，设置不存在的 ready marker，轮询终态后读取串口/末帧/证据并保留会话历史。

### #219：AtomS3 LCD_CAM 探测与 SPI 读回

AtomS3 虽使用 SPI 屏幕，固件仍先探测未接屏的片上 LCD_CAM。0185 接通命令完成及 IRQ 路径；0186 让 RDDID 按总线读时钟推进，并在事务完成时将 RX 锁存进共享 FIFO，避免后续 MMIO 读反复获取首字节。

原版 Snake/UserDemo 指定 GC9107 后均产生 128×128 有效帧并观察 120 秒。整合首轮固定 200 ms 的第四次输入未观察到帧变化，保留 `FAIL`；后续保持输入、最多观察 2 秒，四次均出现可见变化。该观察证明可见响应，未建立四方向游戏状态语义。

证据：[独立显示复测](evidence/issue219-atoms3-display-summary.json)、[整合首败及后续复测](evidence/integration-summary.json)。源码：[显示运行器](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/tests/firmware/atoms3_display/README.md)、[0185](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/patches/qemu-m5stack-peripherals/0185-atoms3-lcdcam-probe.patch)、[0186](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/patches/qemu-m5stack-peripherals/0186-spi-panel-read-cursor.patch)。

### #220：原 PaperColor 的 USB 类型与控制传输

该原版工厂固件暴露 MSC 接口。真实 TinyUSB buffer-DMA/EP0 路径完成设备/配置描述符、地址、配置设置/读回和 `GET_MAX_LUN=00`；StickS3 的 CDC 行编码与 bulk 通路单独回归。该项是限定协议验证，不需要把 CDC 强加给仅 MSC 的固件。

证据：[USB 协议事务](evidence/issue220-papercolor-usb-summary.json)、[整合复测](evidence/integration-summary.json)。复现：[原版固件运行器](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/tests/firmware/papercolor_usb_otg/README.md)。MSC 块读写、后续应用稳定性和物理 USB 未测。

### #224：eFuse 字节序、CRC 和身份声明

Classic ESP32 fixture 修正 factory MAC 字节序及 ROM CRC。原生 Atom Lite/Matrix 三条 IDF API 与服务身份一致，重启服务后历史记录身份不变。没有实际挂载 eFuse 的 Core2/C6 明示 `unprovisioned`；C6 的 AES 元数据对照没有读取 guest MAC，不能冒称已验证。

历史 Evil-Parasite 源码面向初代 AtomS3。同一 BIN 在 AtomS3R 黑屏但停在正常 WAITI，在 AtomS3 GC9107 有 avatar 像素；这不支持把原黑屏直接归因于 PHY 校准回退。未操作攻击功能，未改写上传 NVS 以消除日志。

证据：[独立 eFuse 控制](evidence/issue224-efuse-identity-summary.json)、[最终主线身份及恢复对照](evidence/issue224-integrated-identity-summary.json)、[同 BIN 板型对照](evidence/issue224-board-comparison-summary.json)。复现：[身份探针](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/tests/firmware/esp32_efuse_identity/README.md)。

### #216：C6 AES 子路径修复，整项仍开放

固定 C6 上游基点并加入可重复构建配方；AES 经真实 MMIO、GDMA request 和 IRQ 接线。Nesso/NanoC6 的 NIST CBC、4096 字节跨描述符加解密与 IRQ 通过，旧运行时负控失败。原 Bruce 从 `AES_STATE` 无限等待推进到 LittleFS 错误页，观察约 163.8 秒；这不是完整应用 PASS。Launcher 互斥量、Meshtastic/RFID 异常仍开放。

证据：[C6 控制与原版 Bruce](evidence/issue216-c6-aes-summary.json)。复现：[AES 测试工程](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/tests/firmware/esp32c6_aes/README.md)、[固定构建脚本](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/scripts/bootstrap-c6-runtime.py)。

[后续原版诊断](evidence/issue216-c6-remaining-summary.json)捕获 Launcher mutex owner/current-task 不一致，以及 Meshtastic 的间接调用目标为零；匹配的原始构建元数据不足，尚不能排除模拟器调度或内存破坏贡献。RFID 原因独立未定位，不继承 Meshtastic 的归因。

### #221：Classic 调度实现与中断源读回，Matrix 仍失败

原生构建遗漏了已有 per-vCPU 时间片限制的实际实现；0021 恢复该实现，不改变服务既有默认策略。0184 让六个 DPORT 中断状态寄存器返回真实外设 IRQ level，供原 IDF 中断处理器区分来源。

在最终 main 服务和运行时 `dcb5c9f3f33bab3915348d48ce5dfa35483889ef1255977b2d49df6c17bea8f1` 上，原 Atom Lite 两轮独立冷启观察 121.90/121.85 秒，完整分页串口无 watchdog/Guru，按键输入经 GPIO 到 RMT LED 输出通过。此前组合在重复并行冷启出现 IWDT 的失败保留；两次通过不证明所有启动交错。

同一最终运行时原 Matrix 观察 121.88 秒仍有 CPU0 Wi-Fi watchdog，LED 输出为零。未合入的离线 MAC 候选推进到 `Wifi scan start`，仍没有扫描结果或灯阵输出，不能据此宣布缺失 Wi-Fi 控制器是已证根因。#221 保持开放。证据：[Classic 原版控制、输入及清理](evidence/issue221-classic-factory-summary.json)。

### #222：Core2 原版应用仍未就绪

原 UIFlow 1.15.5 和 HamRadio 0.1.5 在 plain/qemu-wifi、时间片限制候选及 AXP192 板型控制中仍未达到应用就绪。UIFlow 的非黑图像是启动 Logo，不能描述为全黑，也不代表应用已运行；HamRadio 仍为黑帧，串口已到配置文件检查。

UIFlow 有 Flash/cache handoff 指令簇活动，单个忙等或 WAITI 采样不能证明永久死锁；没有匹配 ELF 支持精确源码归因。0179 的 AWS 子路径成功不能转授这些样本。证据：[各控制的固件、运行时、串口和帧](evidence/issue222-core2-remaining-summary.json)。[最终组合独立观察](evidence/issue222-core2-final-summary.json)中，UIFlow 到 60 秒出现启动 Logo、90–120 秒不变；HamRadio 五次采样均黑。相同运行时原 AWS 在 30 秒显示应用首页，只作为显示控制，不转授其他固件通过。

### #223：I2C 生命周期诊断，原版仍失败

原 UserDemo 的 QEMU guest-store instrumentation 捕获 CPU0 I2C ISR 字节写覆盖 CPU1 saved-frame 地址；随后 `retw.n` 读到坏的返回地址。每 CPU 环形计数不提供完整跨核先后次序；BREAK PC 是 DoubleExceptionVector，不是随机截断的直接证据。

最小双核 ESP-IDF 5.5.4 探针独立证明成功同步读取返回后 buffer 仍被 ISR 修改（第 10/75 次）。只在诊断 SDK 将 DONE 通知移到 FIFO 拷贝后，30,000 次读取无后续修改且 errors=0。该 SDK 正控与原 BIN 严格分开，未作为模拟器补丁合入。

原 UserDemo/GPT 仍失败；延迟 I2C 完成的 6 个会话全失败，single+icount 6 个会话仍有 1 个 GPT 失败。失败后保留的非黑帧不能证明动画持续。物理归因和 timeout 分支未完成，因此 #223 保持开放。

证据：[全部失败、候选、写入和正负控](evidence/issue223-i2c-lifetime-summary.json)。复现：[诊断工程与 SDK 对照](https://github.com/m5agent/m5stack-esp-emulator/blob/98287067eaf558576d1120f213d676630d66c2bd/tests/firmware/s3_i2c_lifetime/README.md)。

## 执行身份、验证层级与待补

首次整合 Xtensa 运行时 SHA 为 `d0c0054ae85aafd0eeb271045e81e258899d0f6d2422392d6834cb66c98a784d`，从固定源码重建，仅复用依赖产物。C6 是独立源/构建线，不能继承 Xtensa 结果。各用例的原版/填充 Flash SHA、运行时、串口、帧、协议和清理分别绑定到 evidence，不从服务 running 推断应用就绪。

最终 Xtensa 运行时 SHA 为 `dcb5c9f3f33bab3915348d48ce5dfa35483889ef1255977b2d49df6c17bea8f1`，新增 0021/0184 后独立通过原版 AtomS3 显示与有界输入响应、PaperColor USB EP0、PaperColor/PaperDIY 主动关机和 atomic 探针，见[最终运行时摘要](evidence/final-runtime-summary.json)。

[首次完整 68 例原生矩阵](evidence/native-matrix-first-summary.json)为 66 PASS / 2 FAIL，278 项检查。StackChan/Core2 audio 的初始失败来自就绪前的固定时间截帧；原 Core2 用例在旧基线也失败。加入真实 guest 音频完成串口标记并沿用既有 30 秒有界等待后，相同组成 BIN 在三份运行时通过，PCM、颜色和 PMIC 判据未放宽。最终运行时重跑 StackChan audio 与 Core2 全六例共七例通过，见[保留失败的独立复测](evidence/audio-readiness-summary.json)。没有把首轮 66 例和后续七例拼成一次全新 68 PASS。

| 层级 | 结果 | 依据与限制 |
| --- | --- | --- |
| build | PASS（限定产物） | Xtensa/C6 已执行构建与各自 guest 用例；源码固定至上述最终提交 |
| transport / device_response | PASS（限定路径） | USB EP0、AES/GDMA/IRQ、eFuse API、关机事件；不泛化所有外设 |
| data_behavior | PARTIAL | IOMMU 控制通过；StackChan 原版仍失败 |
| visual_or_physical | PARTIAL / NOT RUN | AtomS3 有效帧及限定输入、Atom Lite 按键→RMT；Core2 应用未就绪，物理未测 |
| final platform suite | PARTIAL | **NOT YET COMPLETED**，尚未写入最终计数 |
| native regression | PARTIAL | 首次完整 68 例为 66 PASS / 2 FAIL，修观察器后最终运行时七例 PASS；最终运行时的新一轮完整 68 例 `NOT RUN` |
| delivery | NOT RUN（本次归档补充） | 本次补充未提交或 push；未评论 issue、未提交 Burner |

**待补：** 最终精确提交的完整平台套件结果。#216/#221/#222/#223 的剩余失败仍开放，不以待补字段代替已知失败。

[机器可读待补项](evidence/pending-final-results-summary.json)与 [run.json](run.json)必须同步更新。所有失败控制都保留，新增成功是独立执行，不覆盖首次失败。

## 复现与回滚

以上固定源码 README 提供所需原版固件 SHA、工具链、控制器/设备配置、命令和判据。普通 checkout 不依赖本机临时缓存；原版公开固件由运行者自行取得并核对哈希。所有用户应用走独立 Device Service 上传/组合/会话路径，在 stop 前取证并使用 `purge=0` 保留历史。

本记录不分发 BIN、ROM、QEMU 可执行文件、可变 Flash 或原始 ZIP；修复不改写原始公开固件。回滚应在独立构建目录恢复已固定的基线源码/配方和相应服务代码，保留现有会话及失败证据；不要替换仍运行的二进制或重置无关工作区。

## 脱敏说明

evidence 均为已审查的派生摘要，不是 raw。未复制端点、宿主路径、凭据、设备 MAC 值、序列号或原始会话标识；保留公开固件 ID、SHA256、协议字节、寄存器地址和已有的会话哈希。[来源清单](evidence/provenance-summary.json)记录每份输入及归档文件的字节数/SHA256。未提交公开二进制或未授权第三方源码。

## 归档准备检查

当前 JSON 解析、UTF-8/BOM、相对链接、敏感值扫描、来源摘要结构一致及 `git diff --check` 均通过。本次修改范围仅本记录和两处索引，未提交或推送。详见 [准备检查](evidence/archive-validation-summary.json)；最终待补项填写后必须重新校验。
