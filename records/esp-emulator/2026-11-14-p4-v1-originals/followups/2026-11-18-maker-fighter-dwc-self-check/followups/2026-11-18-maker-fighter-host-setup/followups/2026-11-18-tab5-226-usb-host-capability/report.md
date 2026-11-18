# 原版运行与能力对照

经隔离 Device Service 的普通制品上传、导入和会话创建请求，分别运行相同的
Tab5 原版应用。固定 GT911/ILI9881C 板型、ROM、C6 伴随固件和 esp-emu 1.1.0。
另一份制品或应用 ELF 没有替换执行内容。

在专用诊断会话给原版 USB 客户端登记和事件等待设置硬件断点。调试器只读原来的
寄存器并正常分离。两轮原版均走到客户端成功登记与事件等待，DWC 核心标识
`0x4f54400a`、`GAHBCFG=0x21`、`HPRT=0x1000`。根端口供电且连接位为零，
没有旧 `usb_dwc_hal_init` 断言，没有取得完整帧。会话原件完整性、ZIP CRC、
清单成员哈希、停机会话、P4/C6 退出、Flash 和租约均已核对。

候选通过 `GET /api/v1/devices/tab5/capabilities` 查询到组件和设备状态
`partial`。端点附件、HID/MSC 枚举和传输仍缺验证，也没有 USB 端点夹具声明。
历史后端的精确 DWC 核心标识断言仍可复现已登记的缺口分类。当前原版不再出现该断言。

复现时使用摘要中的原版 SHA、运行时、板型和 API 版本。经 `/api/v1/artifacts` 上传原件，
`/api/v1/firmware/import` 核对规范化 SHA，再以公开 `qemu` 模式创建 Tab5 会话。
诊断窗口只读 USB 客户端登记、事件等待及 DWC 状态。在停止前保留标准证据 ZIP。
所有结果为 virtual-device validation。USB 外设、应用可交互画面、浏览器和真机未验收。

[原版早期安装与事件等待控制](https://github.com/m5agent/agent-work-logs/blob/923679586152244e76f3992e5305962bf9043ec6/records/esp-emulator/2026-11-14-p4-v1-originals/followups/2026-11-18-maker-fighter-dwc-self-check/followups/2026-11-18-maker-fighter-host-setup/README.md) · [官方后端接口](https://github.com/espressif/esp-emulator/blob/v1.1.0/docs/guides/HOST-INTERFACES.md)
