# ESP Emulator Core2 for AWS ATECC608 报告

## 背景

`RUNTIME-04` 记录 Core2 for AWS 公开 factory firmware 在虚拟设备中停止：
固件访问 ATECC608 的 7-bit address `0x35`，QEMU 板级没有 slave，因此所有
start 都 NACK；CryptoAuthLib 的 `atcab_init` 最终返回 `f0`，firmware 随后
`abort()`，没有应用帧。

目标是让同一公开固件通过实际 I2C command path 完成安全元件初始化并产生
非空应用帧，同时不向仓库分发生产私钥或把测试 config 冒充真实 trust root。

## 根因与实现

根因分为两层：

1. Core2 board I2C bus 缺少 ATECC608 slave 与 CryptoAuthentication framing；
2. 安全元件通过后仍然黑屏，因为 classic ESP32 SPI DMA 把 descriptor
   address 和 start bit 分两次写入，旧模型把 start 写当成地址 `0`；随后
   又把所有 DMA payload 当成像素数据，没有依据 GPIO15 DC 区分 command/data。

`0085-core2-atecc608.patch` 增加：

- 7-bit address `0x35` 的 `m5.atecc608` QOM slave；
- wake token `04 11 33 43`、idle/sleep word；
- CryptoAuthentication count/opcode/parameter/CRC packet；
- CryptoAuthLib CRC16 `0x8005`；
- 32-byte config Read、4-byte lock-word Read 和 Info revision；
- 确定性的 locked config/data zone，revision `00 00 60 02` 和测试 serial；
- classic ESP32 DMA link 地址保存/start 复用、按 descriptor 时 DC 电平分类
  command/data，并避免完成后由 CPU register 路径重复消费。

fixture 数据区为零，不含生产 key、certificate 或 slot secret。

## 执行

使用隔离 QEMU source worktree 和真实 Device Service HTTP：

```bash
./configure --target-list=xtensa-softmmu ... --disable-docs --disable-werror
ninja -C build qemu-system-xtensa

M5_QEMU_XTENSA=/path/to/qemu-system-xtensa \
M5_QEMU_XTENSA_ROM_DIR=/path/to/pc-bios \
python3 platform/tools/serve.py "${DEVICE_SERVICE_PORT}" \
  --state-dir "${STATE_DIR}"

python3 tests/firmware/core2_atecc608/run_service.py \
  --api "${DEVICE_SERVICE_API}/api/v1" \
  --image /path/to/Core2_For_AWS.bin \
  --qemu /path/to/qemu-system-xtensa \
  --attempts 3 \
  --out-dir "${RUN_DIR}"
```

runner 对每个 attempt 执行 artifact upload、firmware composition、visible
session、serial/frame wait、serial/frame/evidence/QOM capture，并以
`purge=0` 停止。输入 SHA 或 QOM/cleanup 条件不符时记录失败，不自动重试。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU 9.2.2 Xtensa 完整链接；平台 `1555 OK + 10 skipped` |
| transport | `PASS` | 真实 `/api/v1` upload/firmware/session/frame/evidence/stop |
| device_response | `PASS` | 三个 session 均命中 `atecc608: ok: 60 02`，无 abort marker |
| data_behavior | `PASS` | trace 包含 32-byte config Read、lock-word Read 和 Info；三轮 frame SHA 相同 |
| visual_or_physical | `PASS`（virtual frame only） | `320x240`、`76,800` nonblack pixels、`160` colors |
| delivery | `PASS` | PR #33、PR CI、main CI、patch reverse-check 和双远端工作记录 |

三个 attempt 的 evidence ZIP 均可解析，停止后 history/firmware identity
保留，QEMU PID 消失，worker lease 释放。runtime coverage、peripheral
catalog、QEMU profiles、project snapshot、compileall、patch reverse-check、
`git diff --check` 和 PR scope 均 PASS。

## 验证边界

该记录只证明公开 firmware 所需 ATECC608 初始化和 identity read 路径，并在
虚拟设备中产生应用帧。它不证明：

- ECDSA key generation、Sign/Verify 或生产 slot 内容；
- 生产 key、certificate、manifest 或 live eFuse trust root；
- side-channel、电气阈值、时序和真实硬件；
- BMI270 缺失造成的独立 firmware 错误或后续 tab/云端业务；
- Core2 legacy UIFlow `RUNTIME-03` 的 startup UI、normal-WDT 或非空帧。

因此公开 firmware 仍保持 `PARTIAL`，但 `RUNTIME-04` 的 bounded
virtual-device 初始化/identity/应用帧门禁已关闭。

## 风险与回滚

模型使用确定性测试身份，不得改称真实 ATECC608 安全保证。回滚合并提交
`622b144619b45cec2a3c90f869e4cc416e32f386` 或撤销 `0085` patch 即可恢复
原 NACK 行为；不涉及持久化生产 key、eFuse 或设备状态迁移。
