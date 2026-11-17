# 原生 Flash 与 UART 崩溃诊断、PaperS3 浏览器触摸复验

本轮分别运行 Cardputer ADV、Nesso N1 和 PaperS3 三条虚拟设备路径。原生 Cardputer ADV 用先前固定的 Xtensa QEMU SHA-256 `68d98b8491b09eeb91fc3c99ee2dd7d2752ac1b6b548bf0c93981f4c225fb05d`，PaperS3 使用浏览器 QEMU WASM SHA-256 `96c7f8baf1d5f2fd760c560a0827ef7305ad06a1cefb28c905d05d796dc540d8`。基线服务源码 `a2148953f1c22a2b2b066780f9c501b3daddcdf0`。整体结果为 `PARTIAL`。

## Cardputer ADV 的 Flash 转储

ESP-IDF v5.5.4 的两个 ESP32-S3 控制固件均在原生 Device Service 会话主动触发 abort。基线和候选的 CRC32 对照使用字节一致的固件、ELF 与 QEMU。三个来宾都报告 `Core dump has been saved to flash.`。该分区使用测试名称 `core_a`，分区类型和子类型为 `01 / 03`，偏移 `0x187000`，长 393,216 字节。独立从会话 8 MiB Flash 读取该区，在基线上重算得到有效的 8,932 字节 CRC32 转储。基线服务在匹配 ELF 下可符号化串口 panic，但 Flash 转储只保留 `flash_reported_saved` 标记。

候选源码 `a890e0e4af7ad9c277dd88b846422f5d1cbb5470` 从会话的实际 Flash 分区解码。CRC32 转储 8,932 字节，SHA256 转储 8,960 字节。用来宾生成的实际字节独立重算尾部校验，并核对 API 的 SHA-256 和保存的转储字节。匹配 ELF 后两个转储各提供五个任务上下文，原始 PC/SP 保持一致。两轮崩溃任务均为 `fixture_fault`，优先级和基础优先级为 2，记录的 TCB 栈占用 512 字节、剩余 3,580 字节。使用 esp-coredump 1.17.2 和 Espressif Xtensa GDB 独立核对，两组 ELF 的任务字段逐项一致。同会话的 API 与 ZIP 提供一致的解码收据，ZIP 没有转储二进制。

无 ELF 或错配 ELF 时仍提供五个上下文，任务元数据与转储符号保持缺省。在另一个仅有串口权限的实际会话，匹配 ELF 后保留串口 panic 符号，同时 Flash 解码返回 `flash_read_denied`。本轮释放可写 Flash 后仍能读取串口标记，Flash 转储入口返回 `flash_unavailable`。另一个 CRC32 会话用 `retain_flash=true` 停止，直接读回的未符号化诊断与该会话运行时逐字段一致，仍有五个上下文。范围限 Cardputer ADV 普通原生 QEMU 的两个受控固件、该分区类型和所列 ELF32 校验格式。[原生证据与独立校验](evidence/cardputer-adv-flash-dump-summary.redacted.json)

## Nesso N1 原生 UART 保存帧

候选 `881445e30c2c306ef5b80249bb37491b54f4b2d7` 使用同一已验证 C6 QEMU SHA-256 `69493c4edccaab5bc24961982ddb9097dda11c9b3418f9cdc0aaa2b27ae865a4`。两份实际 Nesso N1 来宾固件分别从 UART 导出 CRC32 和 SHA256 转储，匹配 ELF 的 RV32 保存帧对照使用独立 Espressif GDB。两个转储中 `main`、`IDLE`、`esp_timer` 分别得到 7、4、5 帧，每帧 PC/SP 与离线结果相同。无 ELF 或错配 ELF 时保持寄存器上下文，调用帧依赖匹配 ELF。

API 和同会话 ZIP 结果相等，停止、释放可写 Flash、重启隔离服务后仍可回读 UART 诊断，两个会话最终都没有占用租约。范围为原生 Nesso N1 上 ESP-IDF RV32 ELF32 UART 转储保存的任务寄存器，以及无 augmentation 的 v3 `.debug_frame` 规则。其他 RISC-V 板、其他运行时、真机与 Flash 转储回溯均为 `NOT RUN`。[帧级对照和归档校验](evidence/nesso-rv32-saved-frames-summary.redacted.json)

## PaperS3 浏览器 GT911 与图标读回

沿用官方 Factory V0.5 原版固件 SHA-256 `d6733a0ca378f95335fa5fba4d4d992fb1dd97c17557b20e9aebfca08ba6d624`、原浏览器 WASM 和 PaperS3 540×960 档案。独立 Chromium 的正常输入桥发送同一坐标 `(113,347)` 的按下和释放。在临时观察副本开启并回读 QMP 的 I²C 事件，解码 GT911 地址 `0x5D` 的状态寄存器 `0x814E` 及坐标寄存器。本轮期望的是会随图标状态切换的 607 像素变化，浏览器测得的外层按压时间仅用于划分观察窗口。

第一轮九次请求取得两次完整变化，均为 300 ms。第二轮用三次相同的可识别画面固定每个图标状态，再对六次输入逐一暂停来宾，比较浏览器共享 RGB565 与独立 QMP 屏幕采集在图标矩形的像素。六次比较差异为零，两次 500 ms 请求通过图标判据。

两轮共四次完整图标切换。每次都有释放前 `0x81` 状态和正确坐标，释放后读到 `0x80`。十次未切换的手势在主机按压窗口无 GT911 事务，释放请求之后首先清除寄存器、读取空报告并再次清除。第一轮最后一次未捕获可分类总线事件。这一顺序与官方驱动在服务间隔过长时丢弃上一帧的分支一致。来宾未及时访问报告的更深原因、实际 IRQ 电平和真实触摸持续时间仍待验证。六次相等的图标矩形限定了这部分共享画面的传输观察。两个 Chromium 实例均优雅停止，剩余 Worker 和 iframe 均为零。[浏览器原始轨迹指纹与清理](evidence/papers3-browser-integrity-summary.json) · [固定版本的 GT911 驱动](https://github.com/m5stack/M5GFX/blob/c6f92dc03226cdc04d67c705a2020f62ad21ad01/src/lgfx/v1/touch/Touch_GT911.cpp#L174)

## 冻结包复验

Device Service API 1.75.0 冻结包当前绑定源码 `63472ab884dc2968904999c75eb6aca91c3f2517`，状态 `PREPARED_NOT_APPLIED`，清单 SHA-256 为 `4809829d4ee01450f1a7f3797bb1b0d13b11cdcc34ffccc99275de79798b55de`。此前 `04646a5d` 包中，两份 Cardputer ADV 受控固件各取得五个任务和同一会话 API/ZIP 收据，停止后释放可写 Flash。首次平台测试保留 5 项失败、14 项错误和 61 项跳过。之后 2,389 项中仅一项失败、10 项跳过，原因是 API sweep 清单的合约 SHA 仍指向旧版本。当前包只更新该清单的版本与哈希字段，取代之前的包。 当前包上的 Cardputer ADV CRC32、SHA256 各完成一次新的实际虚拟 Flash 解码，两份新转储分别再次与独立 Espressif 离线工具的五个任务字段一致。Nesso 两种 UART 格式独立复跑，7/4/5 帧再次与 GDB 一致，API 与 ZIP 相等，服务重启后读回一致，租约归零。旧包第一次 Nesso 的完整 API/ZIP 对比失败，原因未定位。保留的 ZIP 有预期帧数；旧包独立第二次和当前包均通过对比。修正后平台全量套件 2,389 项中 2,379 项通过、10 项跳过。Node 34 组宿主契约通过。[冻结包、复跑及早期测试](evidence/prepared-package-summary.json)

## 复现入口和范围

Cardputer ADV 用仓库崩溃探针、ESP-IDF v5.5.4 和有界数据转储分区分别构建 CRC32 与 SHA256 固件。启动独立 Device Service，会话串口出现写入完成标记后，通过 `/crash` 带正常、错误或无 ELF 读取，在停止前核对受限 Flash 分区及离线 GDB。Nesso 使用仓库的 RV32 UART 崩溃探针、同版 SDK 和匹配 ELF 复现逐帧结果。PaperS3 用相同原版、浏览器公开输入桥和独立 I²C 观察，逐一对照图标读回与 bus 操作。故障归因保持在有证据的控制场景内。物理板卡、触摸机械和光学为 `NOT RUN`。
