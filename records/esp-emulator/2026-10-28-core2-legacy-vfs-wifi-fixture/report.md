# ESP Emulator Core2 legacy VFS 与 WiFi fixture 校正 报告

## 背景

- 来源：`RUNTIME-03` legacy UIFlow 启动与黑帧复核。
- 现象：同一公开固件在裸 QEMU 中长时间停在启动早期，帧为纯黑。
- 目标：确认阻塞来自 guest 固件、QEMU 控制器还是测试夹具，并让后续诊断
  使用与 Device Service 产品路径一致的输入。

## 结论

- 状态：`PARTIAL`
- 根因或关键判断：
  1. 通用 LittleFS 生成的 VFS 不被 legacy guest 接受，guest 重新格式化
     分区，因此注入的 `/flash/boot.py` 从未执行；
  2. 裸 QEMU 诊断没有 `misc.esp32_wifi`，而 legacy 启动会访问
     `0x60033d24` 的 `WIFI_DMA_OUT_STATUS` APB alias；
  3. 修正后可以执行注入的 boot 文件，但系统菜单/setup 和非空帧仍未完成。
- 改动范围：新增 VFS probe、公开证据和当前状态/Backlog/profile 边界校正；
  未修改 guest 固件或 QEMU 产品代码。

## 证据

### 代码或配置

```text
Source firmware: 18d77e28… (16777216 bytes)
Test image:      893d3535… (VFS at 0x520000, size 0x6de000)
VFS payload:     805e1acd… (UIFlow littlefs2 packer)
QEMU:            3b56b49a…
Runtime:         Device Service /api/v1, qemu-wifi, core2-openmac
```

### 执行

- 使用 `/api/v1` 创建可见 session，未直接启动产品功能测试。
- 使用 `M5_CORE2_ICOUNT_SHIFT=5` 和精确 virtual-time pause。
- 在 `120.000000030 s` 获取两核 state 和 frame。
- 同一 corrected fixture 的 normal-WDT control 仍出现
  `TG0WDT_SYS_RESET` / `TG1WDT_SYS_RESET`。
- 最终源码提交的 GitHub Actions
  [`40693004977`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40693004977)
  两个 job 均通过。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU binary 成功构建，平台 `1362` 项通过 |
| transport | `PASS` | Serial 输出 `APIKEY` 与 `CORE2_LEGACY_VFS_BOOT` |
| device_response | `PASS` | guest 读取的 VFS 内容来自注入 payload |
| data_behavior | `PARTIAL` | WiFi-backed Device Service 路径继续执行，但未到 setup/main |
| visual_or_physical | `FAIL` | 320x240 final frame 为 `0` nonblack pixels |

## 验证边界

- 旧无 NIC 黑帧不能作为“到达显示路径后 flush 不完成”的充分证据。
- corrected lane 在 120 秒仍没有 setup/main；不能声称应用启动 PASS。
- normal-WDT 失败位于虚拟运行时，不能外推到物理 watchdog 行为。
- 物理硬件、RF、声学、光学和电气测量均 `NOT RUN`。

## 风险与回滚

- 本记录只改测试夹具、证据和状态文档；回滚为恢复旧 fixture 与文档文本。
- 不提交固件、原始 VFS、设备标识或运行缓存。
