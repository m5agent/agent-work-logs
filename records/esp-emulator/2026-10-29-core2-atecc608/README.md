# ESP Emulator Core2 for AWS ATECC608

- 日期：`2026-10-29`
- 结果：`PASS`（virtual-device validation，限定 ATECC608 初始化/identity 和应用帧）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-04`，[PR #33](https://github.com/m5agent/m5stack-esp-emulator/pull/33)
- 源码版本：`m5stack-esp-emulator@7f4324cc9e8ea54bc97acd5361ce60aa800814e7`
- Base：`0eb8f8fa53f1089d61455796fd1aea8b38de2990`
- 合并提交：`622b144619b45cec2a3c90f869e4cc416e32f386`
- 环境：macOS arm64；隔离构建的 QEMU 9.2.2 Xtensa；真实 Device Service `/api/v1`；虚拟 Core2

## 结论

公开 Core2 for AWS factory firmware 原先在 7-bit address `0x35` 找不到
ATECC608，`atcab_init` 返回 `f0` 后触发 abort。`0085` 增加真实 I2C
command data plane，使用锁定、确定性的测试 config，并同时修复 classic
ESP32 DMA descriptor start 分段写入与 DC command/data 分类。

三个独立 `/api/v1` session 都到达 `atecc608: ok: 60 02`，产生 `320x240`
应用帧，并在停止后保留 evidence/history、释放 lease、清除 QEMU PID。该结果
关闭 `RUNTIME-04` 的 bounded virtual-device 门禁；不代表生产 key、ECDSA
签名、真实 trust root、电气行为或物理硬件验证。

## 关键证据

- 公开 artifact SHA256：
  `22ee8c0f5d3c9640be370cb1a89496ed265b685d573b0e41d62320cf6288ff3a`
- service-normalized firmware SHA256：
  `104062aa0e6f52470f0c7f409d202af5d2dad5c3e5ee8f7e65815508a512ef3c`
- QEMU SHA256：
  `a802d6a358b6bccb1e9d856b6179ca7245101751a627b7b6f3ddadc3a73fb5b0`
- QEMU patch SHA256：
  `797420fcb1b487f06e8e5fa1cec746ec0fd47a2316f18d10fd28e928c0872059`
- runner SHA256：
  `6ff1dacee453bda12e6c47803bb9270c7e39709a30113cc9d379b56bff35b936`
- 三次 frame 均为 `76,800` nonblack pixels、`160` colors，PNG SHA256：
  `f373994099403fea3b0e42d0dbf9b0486d2d9306cbb9c6cb27455794b602eb10`
- 平台套件：`1555 OK + 10 skipped`

源码证据：

- [ATECC608 evidence](https://github.com/m5agent/m5stack-esp-emulator/blob/622b144619b45cec2a3c90f869e4cc416e32f386/docs/evidence/2026-10-29-core2-atecc608/README.md)
- [machine summary](https://github.com/m5agent/m5stack-esp-emulator/blob/622b144619b45cec2a3c90f869e4cc416e32f386/docs/evidence/2026-10-29-core2-atecc608/summary.json)
- [QEMU patch](https://github.com/m5agent/m5stack-esp-emulator/blob/622b144619b45cec2a3c90f869e4cc416e32f386/patches/qemu-m5stack-peripherals/0085-core2-atecc608.patch)
- [service runner](https://github.com/m5agent/m5stack-esp-emulator/blob/622b144619b45cec2a3c90f869e4cc416e32f386/tests/firmware/core2_atecc608/run_service.py)

## 文件

- `report.md`：根因、实现、执行、验证和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏机器摘要

## 未覆盖项

- production key、certificate、slot provisioning 和 live trust root；
- ECDSA key generation/signing 和安全元件侧信道；
- ATECC608 电气、时序和物理硬件验证；
- 该公开 firmware 的 BMI270 和后续所有 tab/云端行为；
- Core2 legacy UIFlow `RUNTIME-03` 的 normal-WDT、setup/REPL 和非空应用帧。
