# ESP Emulator 社区固件问题修复与复测报告

## 背景与范围

公开 [#216](https://github.com/m5agent/m5stack-esp-emulator/issues/216) 至 [#224](https://github.com/m5agent/m5stack-esp-emulator/issues/224) 报告了 C6 启动、PaperColor 宿主崩溃/USB/关机、AtomS3 黑屏、经典 Atom 看门狗、Core2 黑屏、StackChan 栈破坏及 eFuse 身份问题。本轮要求沿原版固件和真实控制器路径复现、修复和保留失败证据，不提交 Burner。

本报告源码快照固定为 [`cf232dbcc93adacab224d6d2fce44c1f55ed0894`](https://github.com/m5agent/m5stack-esp-emulator/commit/cf232dbcc93adacab224d6d2fce44c1f55ed0894)，基线为 `676ae67c67941b976be799782ef4af40827b666d`。最终提交及仍进行的 #221/#222 结论待整合者补齐。本记录是公开材料的本地草稿，未提交或推送。

## 根因、改动与实际结果

### #217：共享 IOMMU 的异核 TLB flush

共享 S3 cache IOMMU 在修改映射的 CPU 上通知所有订阅者，旧实现直接清理另一个正在执行的 vCPU 的软件 TLB，可与 atomic lookup 竞争。0182 将异核失效排入目标 vCPU 的工作队列，保留本核/启动前同步处理和 atomic 检查。

同一双核探针旧运行时 3/3 宿主失败，修复后 2/2 完成 200,000 次重映射。原 PaperColor factory 两轮 120 秒宿主存活；首次整合运行时再观察 300.74 秒无宿主退出，但记录 1 次 guest 断言及 2 次 `Rebooting`。结论仅限宿主崩溃修复，应用仍 `PARTIAL`。

证据：[cache/atomic 控制](evidence/issue217-cache-atomic-summary.json)、[整合复测](evidence/integration-summary.json)。源码：[0182](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/patches/qemu-m5stack-peripherals/0182-tcg-iommu-vcpu-flush.patch)、[可运行探针](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/tests/firmware/s3_cache_atomic/README.md)。

### #218：主动关机与故障终态分离

服务同时读取 QMP `SHUTDOWN` 的 guest/reason 和 `query-status=shutdown`，使用 `-no-shutdown` 留出末帧采集窗口，再走已有进程和 lease 清理。退出码、日志文字、白屏都不是关机原因的替代证据。

原 PaperColor/PaperDIY BIN 在故意缺失的 ready marker 条件下均以 `stopped/guest_poweroff` 收口，末帧可读。批量 runner 返回 `PARTIAL/guest_poweroff`、`application_ready=false`。PaperDIY 首次短窗未观察到关机的结果保留，默认时间线另行复测。

证据：[关机摘要](evidence/issue218-poweroff-summary.json)、[整合复测](evidence/integration-summary.json)。复现入口：[Device Service](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/platform/tools/device_service.py)：原始 artifact → merged firmware → qemu session，设置不存在的 ready marker，轮询终态后读取串口/末帧/证据并保留会话历史。

### #219：AtomS3 LCD_CAM 探测与 SPI 读回

AtomS3 虽使用 SPI 屏幕，固件仍先探测未接屏的片上 LCD_CAM。0185 接通命令完成及 IRQ 路径；0186 让 RDDID 按总线读时钟推进，并在事务完成时将 RX 锁存进共享 FIFO，避免后续 MMIO 读反复获取首字节。

原版 Snake/UserDemo 指定 GC9107 后均产生 128×128 有效帧并观察 120 秒。整合首轮固定 200 ms 的第四次输入未观察到帧变化，保留 `FAIL`；后续保持输入、最多观察 2 秒，四次均出现可见变化。该观察证明可见响应，未建立四方向游戏状态语义。

证据：[独立显示复测](evidence/issue219-atoms3-display-summary.json)、[整合首败及后续复测](evidence/integration-summary.json)。源码：[显示运行器](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/tests/firmware/atoms3_display/README.md)、[0185](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/patches/qemu-m5stack-peripherals/0185-atoms3-lcdcam-probe.patch)、[0186](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/patches/qemu-m5stack-peripherals/0186-spi-panel-read-cursor.patch)。

### #220：原 PaperColor 的 USB 类型与控制传输

该原版工厂固件暴露 MSC 接口。真实 TinyUSB buffer-DMA/EP0 路径完成设备/配置描述符、地址、配置设置/读回和 `GET_MAX_LUN=00`；StickS3 的 CDC 行编码与 bulk 通路单独回归。该项是限定协议验证，不需要把 CDC 强加给仅 MSC 的固件。

证据：[USB 协议事务](evidence/issue220-papercolor-usb-summary.json)、[整合复测](evidence/integration-summary.json)。复现：[原版固件运行器](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/tests/firmware/papercolor_usb_otg/README.md)。MSC 块读写、后续应用稳定性和物理 USB 未测。

### #224：eFuse 字节序、CRC 和身份声明

Classic ESP32 fixture 修正 factory MAC 字节序及 ROM CRC。原生 Atom Lite/Matrix 三条 IDF API 与服务身份一致，重启服务后历史记录身份不变。没有实际挂载 eFuse 的 Core2/C6 明示 `unprovisioned`；C6 的 AES 元数据对照没有读取 guest MAC，不能冒称已验证。

历史 Evil-Parasite 源码面向初代 AtomS3。同一 BIN 在 AtomS3R 黑屏但停在正常 WAITI，在 AtomS3 GC9107 有 avatar 像素；这不支持把原黑屏直接归因于 PHY 校准回退。未操作攻击功能，未改写上传 NVS 以消除日志。

证据：[独立 eFuse 控制](evidence/issue224-efuse-identity-summary.json)、[最终主线身份及恢复对照](evidence/issue224-integrated-identity-summary.json)、[同 BIN 板型对照](evidence/issue224-board-comparison-summary.json)。复现：[身份探针](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/tests/firmware/esp32_efuse_identity/README.md)。

### #216：C6 AES 子路径修复，整项仍开放

固定 C6 上游基点并加入可重复构建配方；AES 经真实 MMIO、GDMA request 和 IRQ 接线。Nesso/NanoC6 的 NIST CBC、4096 字节跨描述符加解密与 IRQ 通过，旧运行时负控失败。原 Bruce 从 `AES_STATE` 无限等待推进到 LittleFS 错误页，观察约 163.8 秒；这不是完整应用 PASS。Launcher 互斥量、Meshtastic/RFID 异常仍开放。

证据：[C6 控制与原版 Bruce](evidence/issue216-c6-aes-summary.json)。复现：[AES 测试工程](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/tests/firmware/esp32c6_aes/README.md)、[固定构建脚本](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/scripts/bootstrap-c6-runtime.py)。

### #223：I2C 生命周期诊断，原版仍失败

原 UserDemo 的 QEMU guest-store instrumentation 捕获 CPU0 I2C ISR 字节写覆盖 CPU1 saved-frame 地址；随后 `retw.n` 读到坏的返回地址。每 CPU 环形计数不提供完整跨核先后次序；BREAK PC 是 DoubleExceptionVector，不是随机截断的直接证据。

最小双核 ESP-IDF 5.5.4 探针独立证明成功同步读取返回后 buffer 仍被 ISR 修改（第 10/75 次）。只在诊断 SDK 将 DONE 通知移到 FIFO 拷贝后，30,000 次读取无后续修改且 errors=0。该 SDK 正控与原 BIN 严格分开，未作为模拟器补丁合入。

原 UserDemo/GPT 仍失败；延迟 I2C 完成的 6 个会话全失败，single+icount 6 个会话仍有 1 个 GPT 失败。失败后保留的非黑帧不能证明动画持续。物理归因和 timeout 分支未完成，因此 #223 保持开放。

证据：[全部失败、候选、写入和正负控](evidence/issue223-i2c-lifetime-summary.json)。复现：[诊断工程与 SDK 对照](https://github.com/m5agent/m5stack-esp-emulator/blob/cf232dbcc93adacab224d6d2fce44c1f55ed0894/tests/firmware/s3_i2c_lifetime/README.md)。

## 执行身份、验证层级与待补

首次整合 Xtensa 运行时 SHA 为 `d0c0054ae85aafd0eeb271045e81e258899d0f6d2422392d6834cb66c98a784d`，从固定源码重建，仅复用依赖产物。C6 是独立源/构建线，不能继承 Xtensa 结果。各用例的原版/填充 Flash SHA、运行时、串口、帧、协议和清理分别绑定到 evidence，不从服务 running 推断应用就绪。

| 层级 | 结果 | 依据与限制 |
| --- | --- | --- |
| build | PASS（限定产物） | Xtensa/C6 已执行构建与各自 guest 用例；最终整合提交待补 |
| transport / device_response | PASS（限定路径） | USB EP0、AES/GDMA/IRQ、eFuse API、关机事件；不泛化所有外设 |
| data_behavior | PARTIAL | IOMMU 控制通过；StackChan 原版仍失败 |
| visual_or_physical | PARTIAL / NOT RUN | AtomS3 有效帧及限定输入；Core2 案例仍待对照，物理未测 |
| final platform suite | PARTIAL | **PENDING_FINAL_RESULT**，尚未写入最终计数 |
| final native matrix | PARTIAL | **PENDING_FINAL_RESULT**，计划 68 项，不能提前写 PASS |
| delivery | NOT RUN（本归档准备） | 未提交、未 push、未评论 issue、未提交 Burner |

**#221 PENDING_FINAL_REPAIR_AND_VALIDATION：** Atom Lite/Matrix 原版厂测看门狗修复/复测由整合者继续，待补最终源码、同 BIN ≥120 秒及输入证据。

**#222 PENDING_FINAL_ATTRIBUTION_AND_COMPARISON：** Core2 原 UIFlow/HamRadio 在准备归档时仍黑；候选失败、AXP192 板型对照和最终归因由整合者补齐。未把黑屏直接定性为固件缺陷。

[机器可读待补项](evidence/pending-final-results-summary.json)与 [run.json](run.json)必须同步更新。所有失败控制都保留，新增成功是独立执行，不覆盖首次失败。

## 复现与回滚

以上固定源码 README 提供所需原版固件 SHA、工具链、控制器/设备配置、命令和判据。普通 checkout 不依赖本机临时缓存；原版公开固件由运行者自行取得并核对哈希。所有用户应用走独立 Device Service 上传/组合/会话路径，在 stop 前取证并使用 `purge=0` 保留历史。

本记录不分发 BIN、ROM、QEMU 可执行文件、可变 Flash 或原始 ZIP；修复不改写原始公开固件。回滚应在独立构建目录恢复已固定的基线源码/配方和相应服务代码，保留现有会话及失败证据；不要替换仍运行的二进制或重置无关工作区。

## 脱敏说明

evidence 均为已审查的派生摘要，不是 raw。未复制端点、宿主路径、凭据、设备 MAC 值、序列号或原始会话标识；保留公开固件 ID、SHA256、协议字节、寄存器地址和已有的会话哈希。[来源清单](evidence/provenance-summary.json)记录每份输入及归档文件的字节数/SHA256。未提交公开二进制或未授权第三方源码。

## 归档准备检查

当前 JSON 解析、UTF-8/BOM、相对链接、敏感值扫描、来源摘要结构一致及 `git diff --check` 均通过。修改范围仅本记录和两处索引，未提交或推送。详见 [准备检查](evidence/archive-validation-summary.json)；最终待补项填写后必须重新校验。
