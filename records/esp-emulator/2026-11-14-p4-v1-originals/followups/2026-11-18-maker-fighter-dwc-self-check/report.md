# 同原版 USB 自检和出帧复验

## 基线

[#226](https://github.com/m5agent/m5stack-esp-emulator/issues/226) 记录同一 Maker Fighter 1.4 原版曾在 esp-emu 0.50.0 的原生 P4 上于 `usb_dwc_hal_init()` 反复断言。之后的 [1.0.0 复验](../../README.md) 观察 60.516 秒、80 次 ROM 启动和 79 次较早的旧 P4 CSR 指令异常，尚未到 USB 自检。该两段历史证据保留。

这次使用 [Device Service 源码 c7e25be5](https://github.com/m5agent/m5stack-esp-emulator/commit/c7e25be5410d3a9968107bc7a0cab5acb9d708bc)、版本 1.91.0，以及 [esp-emu 1.1.0](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) 原生 Tab5 后端。该版本文档所列 USB OTG 支持方向为 guest 设备与模拟器内建主机。[固定版 README](https://github.com/espressif/esp-emulator/blob/34ba27a6e5a3da41743fc861b462cf2452f0ca28/README.md)

原版为 6,518,928 字节，SHA-256 `d96962362b262bcc4e5abcf6a720a2de1a53f0869c87916fd3f798eb845e08b6`。标准导入得到 16 MiB、SHA-256 `4da826b590d879ccb7728b20257c1847a8093868eb2752600994f1242438bdeb`。三次都走 GT911/ILI9881C 档案、原生 GT911 Part、真实 P4 rev0 ROM、原有修订 eFuse 种子及 C6 协处理器进程。完整指纹见 [有界记录](evidence/same-bin-usb-summary.json)。

## 三次隔离执行

| 执行 | 观察 | 数据 |
| --- | --- | --- |
| A1 | 无调试器，42.002 秒 | ROM 串口 223 字节，1 次 ROM 启动、0 次软件复位，0 次旧 CSR 故障标记、0 次 GSNPSID 断言、0 有效帧 |
| A2 | 24.002 秒，单独会话读取三个双核 PC 样本，各次均正常 detach | hart 0 始终位于紧随 `wfi` 的原版 IRAM 指令；hart 1 三次位于原版 XIP 映射内的半字读写和可选字节交换循环，步长为 1,440 字节，循环行数为 1,280。仍无有效帧 |
| A3 | 24.000 秒，单独会话在原版 DWC 自检两个分支设硬件断点 | 原指令 `0x40109372` 以 `s0+0x40` 读核心标识，`s0=0x50000000`。接受分支 `0x401093aa` 命中，`a4=0x4f54400a`；拒绝分支 `0x4010938a` 未命中。移除断点并正常 detach。仍无有效帧 |

A2 观察到原应用指令，尽管三个执行的捕获 UART 都只打印 ROM 段。A3 读取 guest 实际加载的值并命中原固件的接受分支，证明这一板型和运行时组合下越过旧 GSNPSID 阻塞点。A2 的内存循环本身没有证实 DSI 输出路径，未定位无帧原因。

每次在停止前取得同会话 ZIP，逐项验证 5 个清单项的长度及 SHA-256、归档 CRC、16 MiB Flash 长度与原应用分区逐字节一致。停止后三个会话均为 `stopped`，可写 Flash 已释放，活跃 lease 为零，所属 P4、C6 和服务进程均退出。

## 复现

1. 依照 [固定版本 Device Service 合约](https://github.com/m5agent/m5stack-esp-emulator/blob/c7e25be5410d3a9968107bc7a0cab5acb9d708bc/docs/device-service.openapi.yaml) 启动独立实例、配置精确 1.1.0 后端并仅准入本条目 normalized SHA；板型配置为 `gt911-ili9881c`，加载精确原生 GT911 Part。
2. 通过 `POST /api/v1/artifacts` 上传原版二进制，`POST /api/v1/firmware/import` 导入 `tab5`，用 `POST /api/v1/sessions` 创建 `device_id=tab5`、`runtime=qemu`、`ttl_seconds=120` 会话。每臂创建独立冷会话。观察 UART、同会话 `frame.png?max_age_ms=0&orient=panel` 和 `crash`。
3. A1 不连接调试器；A2 单独运行，使用该会话 P4 GDB 端点执行 `info threads`，分别读取两核的 PC、RA、SP 和当前指令后 detach。A3 在应用阶段前连接，设 `hbreak *0x401093aa` 与 `hbreak *0x4010938a`，`continue` 后读取 PC、a4、s0、ra，删除断点并 detach。A3 不写 guest 寄存器、Flash 或 MMIO。
4. 每次用 `/evidence?include=manifest,serial,frames,logs,flash` 保全同会话证据，按 `?purge=0&retain_flash=0` 停止会话并核对清理。原固件、运行时和仓库源码没有修改，无适用回滚。

后续验收：获得原应用有效帧，独立证明 `usb_host_install()` 返回及 guest Host 端点完成 HID 或 MSC 枚举和一次实际传输。当前这些验收分别为 `NOT ESTABLISHED` 和 `NOT RUN`，没有为本次试验连接 USB 设备。物理硬件、浏览器与 Burner 提交均未执行。公开记录保留摘要、输入身份和原始材料哈希，省略本地路径、会话细节、进程标识和原始内容。
