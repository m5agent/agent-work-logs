# Maker Fighter 1.4 原版 Host 软件路径与控制器状态

本记录延续 [同一原版 DWC 自检](../../README.md)。固定 [Device Service 1.92.0 源码 1c2eb72d](https://github.com/m5agent/m5stack-esp-emulator/commit/1c2eb72d3b7e517e2ceb487c408708a5b800a8c8)，沿用相同的 [esp-emu 1.1.0](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) 二进制，GT911/ILI9881C、原生 GT911 Part、P4 rev0 ROM、修订 eFuse 种子与 C6 进程。原版文件 6,518,928 字节，SHA-256 `d96962362b262bcc4e5abcf6a720a2de1a53f0869c87916fd3f798eb845e08b6`，标准导入 16 MiB Flash 为 `4da826b590d879ccb7728b20257c1847a8093868eb2752600994f1242438bdeb`。

| 冷启动会话 | 同会话观察 | 结果 |
| --- | --- | --- |
| A4，只读硬件断点 | 原应用调用实际 `usb_host_install()`：入口 `0x400fc9b6`，期间原 DWC 接受分支 `0x401093aa` 的 `a4=0x4f54400a`，返回指令 `0x400fca12` 的 `a0=0`，返回地址始终为原调用点下一条 `0x400b6c9a` | Host 安装 **PASS** |
| A5，只读硬件断点与快照 | 应用在 `0x400b6cc8` 调用 `usb_host_lib_handle_events()`，超时参数 `0xffffffff`；原应用在 `0x400b78bc` 接到 `usb_host_client_register()` 返回值 `0`；应用 USB 已启动标记为 1，客户端句柄非空 | 应用事件等待与客户端注册 **PASS** |
| A6，无调试 | 42.000 秒，UART 223 字节、仅一个 ROM 启动，零软件复位、零旧断言、零有效 DSI 帧 | 有界冷启动观察；应用画面未建立 |

A5 在客户端注册节点另读了 DWC MMIO。根控制器 `GSNPSID=0x4f54400a`、`GAHBCFG=0x21`、`GINTSTS=0x4000020`、`HPRT=0x1000`。Host 配置打开了 DMA 和全局中断，根端口报告供电且连接位为 0。此次取得的是状态寄存器和原程序执行证据，端点 DMA 完成、中断交付与 USB 按键响应待验证。[ESP-IDF v5.5.4 DWC LL](https://github.com/espressif/esp-idf/blob/v5.5.4/components/hal/esp32p4/include/hal/usb_dwc_ll.h)

函数身份从原 BIN 中的指令、错误字符串与 [ESP-IDF v5.5.4 USB Host 源码](https://github.com/espressif/esp-idf/blob/v5.5.4/components/usb/usb_host.c) 交叉确认。两段调试都在冷启动前段连接自带 GDB 端点，使用硬件断点读取 guest 实际寄存器、RAM 和 MMIO，移除断点后正常 detach。关键证据包括原始结果摘要、每臂 ZIP 与调试记录的 SHA-256，详细结构见 [有界证据](evidence/host-setup-summary.json)。三次观察均无独立应用 UART 标记，无有效画面，因此原版显示就绪仍待定位。

## 复现与剩余验收

1. 按 [固定服务合约](https://github.com/m5agent/m5stack-esp-emulator/blob/1c2eb72d3b7e517e2ceb487c408708a5b800a8c8/docs/device-service.openapi.yaml) 启动独立实例，准入上述 normalized SHA。通过标准 artifacts、firmware/import 和 sessions API 启一个新的 Tab5 `runtime=qemu` 会话。三臂各重新导入启动，USB 口为空。
2. A4 使用 `hbreak *0x400fc9b6`、`hbreak *0x401093aa` 和 `hbreak *0x400fca12` 分别读取原调用、原自检值和 ABI 返回寄存器。A5 使用 `hbreak *0x400b6cc8` 与 `hbreak *0x400b78bc`，记录等待参数、返回与 MMIO。A6 在无附加 debugger 的服务会话观察 42 秒。
3. 停止前取得 `/evidence?include=manifest,serial,frames,logs,flash`，逐项校验 ZIP CRC、五项清单的长度和 SHA、Flash 长度与应用分区原字节。停止返回 `stopped`，可写 Flash 已释放、活跃租约为 0、独立服务和其 P4/C6 子进程均退出。

固定 [v1.1.0 README](https://github.com/espressif/esp-emulator/blob/34ba27a6e5a3da41743fc861b462cf2452f0ca28/README.md) 记录的是 guest USB 设备加内建虚拟主机，而已检查的发行 CLI 和 [Part ABI](https://github.com/espressif/esp-emulator/blob/34ba27a6e5a3da41743fc861b462cf2452f0ca28/proto/PART_ABI.md) 未提供给 guest USB Host 挂载 HID/MSC 的接口。仍需实际 peer 连接、枚举成功、至少一个端点完成传输，并另验原版可见画面。物理硬件和浏览器均未执行。此次无源码、固件或常驻服务变更，也无 Burner 提交。
