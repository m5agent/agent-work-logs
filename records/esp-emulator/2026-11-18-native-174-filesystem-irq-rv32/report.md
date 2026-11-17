# Device Service 1.74 原生复验与输入时序追踪

1.74 虚拟设备验收使用源码 `e822150c90a99b33fbb0f437db611c04f3e1e6e3`。Xtensa QEMU SHA-256 为 `68d98b8491b09eeb91fc3c99ee2dd7d2752ac1b6b548bf0c93981f4c225fb05d`，Nesso N1 所用原生 C6 运行时 SHA-256 为 `69493c4edccaab5bc24961982ddb9097dda11c9b3418f9cdc0aaa2b27ae865a4`。整体为 `PARTIAL`。本轮后续仅修订文档和项目快照，发行包目标提交 `a2148953f1c22a2b2b066780f9c501b3daddcdf0` 的 `platform/`、`patches/`、`scripts/` 和 `tests/` 与实测提交逐档一致。

| 路径 | 结果 | 观察 |
| --- | --- | --- |
| StickS3、Dial 和 Cardputer ADV 内部文件系统 | PASS | LittleFS 三组、SPIFFS 一组，在 12 个独立会话中校验分区导出、重启后回读与重新导入。 |
| Cardputer GP-SPI IRQ | PASS | 同一探针基线与候选对照复现旧版串扰，最终源码上每个控制器只清自身的中断。 |
| 原版 NC1020 | PARTIAL | 206/206 个 ROM bank、512 KiB NOR 和同会话 G0 保存通过，337 次心跳后报告仍无首个完整画面标记。 |
| Nesso N1 UART RV32 转储 | PASS | CRC32 和 SHA256 两个受控崩溃各解析三个 task context，停机及服务重启后仍可回读。 |
| 较早的原版 Dial / PaperS3 | PARTIAL | Dial 快速选曲漏采样跨三种时钟复现；PaperS3 原生和浏览器的所测工厂应用点击结果均不稳定。 |

## 内部数据分区跨会话

每个板卡和文件系统组合都经历三个独立 lease。先用干净种子镜像启动，来宾读到种子文件、写出证明文件、卸载重挂载并读回。停止前证据 ZIP 固定写后分区，停止并释放 Flash 后重启服务，调用 `GET /sessions/{id}/storage/filesystem` 与 `POST /sessions/{id}/storage/filesystem/export` 读取清单及导出，由已保存元数据保留同一 SHA。随后新会话使用 1 MiB 导出分区作为 `storage.filesystem.image_artifact_id`，来宾读回证明文件。另一个新会话重新使用干净种子，确认此前文件不会串入。

StickS3 使用 ESP-IDF 5.5.4 的 LittleFS，Dial 和 Cardputer ADV 使用 ESP-IDF 6.1.1 的 LittleFS，Cardputer ADV SPIFFS 使用 ESP-IDF 5.5.4。导入前文件数分别为 LittleFS 1→2 和 SPIFFS 2→3，重新使用种子后各自回到 1 和 2。12 次结果都保持目标分区外 Flash 字节及原工件不变。导出内容在各证据 ZIP 和停止后重复导出中一致。该结果覆盖已声明的测试分区和来宾文件操作。[文件、串口和数据哈希](evidence/filesystem-across-lease-summary.redacted.json)

## Cardputer GP-SPI 中断和原版 NC1020

同一探针对 SPI2 和 SPI3 指定不同 CPU 中断掩码。旧冻结运行时两条 host 的传输都产生 `00000300`，清另一个 host 的 IRQ 后自己的 CPU pending 也掉为零，而原始状态仍然为 1。0224 的候选及最终 `e822150c` 运行分别得到 `00000100`、`00000200`。清另一个 host 不影响自己的 pending，清自身后归零。较早同一 IRQ 候选的 K132 Factory v0.08、v0.09 与 UIFlow2 v2.5.4 都有预期截图及按键响应。该原厂固件回归有自己的执行身份。[同探针基线与候选](evidence/cardputer-irq-ab-summary.redacted.json) · [最终提交复验](evidence/e822-nc1020-irq-summary.redacted.json)

最终构建的原版 NC1020 使用相同原版合并镜像和 FAT16 工件。应用产生 337 次心跳，Flash 写入的 206 个 ROM bank 和 512 KiB NOR 与合成输入逐字节一致；同会话 G0 留下 99,384 字节。三张 240×135 样本的 SHA 一致，各有 120 个非黑像素。没有首次完成 LCD 绘制标记。较早独立候选的原版首次完整绘制复验也保留了无追踪残差。中断路由独立通过，原版画面仍是独立待定位项。[原版运行收据](evidence/e822-nc1020-irq-summary.redacted.json)

另用未修改的 ESP-IDF v5.4.1 SPI LCD 异步驱动跑最小探针，探针无 SD 流量。CPU0 初始化 SPI2 并执行全部颜色完成回调。同核提交、回调、取回结果在旧版和最终版三次执行均为 960/960/960。将绘制和读取完成结果放到 CPU1 后，旧版达到 299/299/298，最终版第一次为 603/603/602，两次都触发 6 秒来宾观察超时。相同最终构建第二次完整达到 960/960/960，属于间歇现象。失败时末行已进入 CPU0 回调，CPU1 等待完成结果。ESP-IDF 在回调之后才调用 `xQueueSendFromISR`，因此范围限于回调到结果返回之间。尚未验证是否成功入队或唤醒，也未确定原版 NC1020 的阻塞点。[跨核摘要](evidence/lcd-cross-core-summary.redacted.json) · [ESP-IDF SPI 完成路径](https://github.com/espressif/esp-idf/blob/4c2820d377d1375e787bcef612f0c32c1427d183/components/esp_driver_spi/src/gpspi/spi_master.c#L953-L959)

## Nesso N1 RISC-V 转储

独立会话在精确 C6 二进制上执行 ESP-IDF UART 转储的 CRC32 和 SHA256 控制固件。两个转储分别为 3,084 和 3,112 字节，均解析 `main`、`IDLE`、`esp_timer` 三个任务。崩溃任务 `main` 的优先级和基础优先级为 1，按保存的 TCB 栈边界得到已用 288 字节和可用 3,804 字节。两轮都核对原始 UART、同会话 API 与 ZIP、离线解析和服务重启后的诊断。未上传 ELF 或传入错误 ELF 的对照均不出现符号。范围为普通原生 Device Service 的 Nesso N1、ESP32-C6 RISC-V 和所列两种格式，实机、其他 C6 设备和浏览器为 `NOT RUN`。[任务、运行时与包校验](evidence/nesso-rv32-summary.redacted.json)

## 较早的 Dial 与 PaperS3 时序诊断

以下输入诊断的源码为 `8c65905e466c69a62239371f1fcd254c183b0712`。Dial 用同一 R1F30 原版、虚拟 GPIO41/40 与 PORT.B AudioPlayer。35 ms 三个时钟组均为 7/7。显式 5 ms 的默认时钟、icount shift 3 与 shift 5 分别为 6/7、6/7、4/7。每组都曾有 −16 格动作从第 2 轨选到第 1 轨，预期第 7 轨，来宾实际 UART 命令为 `04fb0306000109`。这三次 64 个相位均有序，其中各有一个相位窗口没有 GPIO_IN1 读。两个 icount 对照的间隔精确为 5.000 ms。1,716 次观察的 GPIO40/41 过渡中 IRQ 类型、使能和 pending 都为 0。根因尚需继续区分固件轮询和更深时序因素。实体旋钮和听感为 `NOT RUN`。[逐时钟摘要](evidence/dial-clock-summary.json) · [IRQ 摘要](evidence/dial-gpio-irq-summary.json)

PaperS3 在相同原版 Factory V0.5 的蜂鸣器图标坐标测试 150、300、500 ms 请求。精确冻结原生运行时通过 4/9，有 GT911 观察的原生运行通过 5/9。原生观察中每次都确认来宾清除按下报告和空报告；其中两条漏点的第一次清除发生于释放后，清除了正确锁存的按下报告。一次漏点仍读取了按下与空报告，所以两条清除记录只能解释一部分观察。另一次原生观察启动缺少仿真辅助组件，未分配来宾；补齐后复跑取得上述结果。浏览器 WebAssembly 的原版通过独立输入桥接运行，按下和释放均接受，使用原生 607 像素差的同一图标判据为 0/9。浏览器缺少来宾 I²C 观察，外层延时不能换算为来宾触摸时长。三个路径各自保留证据和清理结果。[冻结原生](evidence/papers3-frozen-native-summary.json) · [GT911 观察](evidence/papers3-gt911-summary.json) · [浏览器](evidence/papers3-browser-summary.json) · [驱动清除逻辑](https://github.com/m5stack/M5GFX/blob/c6f92dc03226cdc04d67c705a2020f62ad21ad01/src/lgfx/v1/touch/Touch_GT911.cpp#L174)

## 复现与验收边界

在独立 Device Service 用 `/artifacts` 和 `/firmware` 导入固件，按摘要创建隔离会话。内部文件系统使用固件实际数据分区格式、标签、几何和分区大小。Cardputer IRQ 使用源码 `tests/firmware/spi_sd_media/cardputer_irq_route` 的同一探针，串口要验证 CPU pending 和 IRQ acknowledge。NC1020 附加相同 FAT16 工件并核对同会话 Flash、串口和画面。Nesso 的两个 UART 探针使用固定 SDK 和各自精确匹配 ELF。停止前保存原生 evidence ZIP，停止时保留会话历史并释放可写 Flash。浏览器诊断保留自己的输入、帧和 Worker 清理，不能套用原生结果。

原生补丁栈核对 170 层正向、170 层反向，跟踪输入逐项比对 10,450 个，固定上游恢复为干净源码。平台套件 2,382 项中 2,372 通过、10 跳过，Node 的 34 组宿主契约、23 项文档契约、四项生成校验与 scope 通过。冻结 1.74 包已暂存，清单 SHA-256 为 `d3bf8e156e702c7945b9a112eb12c52c5eb9813ae24930fe93102975d60f752f`，11,678 项独立重算匹配。隔离包启动成功，1.74 API 与源码逐字节一致。GitHub Actions 对发行提交的 `platform-contracts` 和 `network-namespace-policy` 均通过。[构建检查](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44140040578)物理设备、声学和射频为 `NOT RUN`。[原生源码核对](evidence/native-stack-audit-summary.json) · [验收套件](evidence/release-validation-summary.json)
