# 公网运行时 Issue #1 验证与解决报告

## 背景

Issue #1 报告第三方无法按 README 和补丁说明从公网重建 QEMU 后端，进而无法
独立验证 Device Service、reference-ready 设备和 Tab5 能力。

## 复现结果

### 失效基线

`espressif/qemu` GitHub API 对
`da100c909249926b9f4458f18e4f2d216d08f51a` 返回 `422 No commit found`。
该对象只存在于开发 clone 的本地历史中，不应作为公开应用基线。

### 补丁快照互斥

在公开 `esp-develop-9.2.2-20260417` 上应用
`zqqf16/M5StopWatch-QEMU` v0.1.0 的五个补丁和本仓 stopwatch patch 后：

- multiboard patch 在 `hw/gpio/esp32_gpio.c`、`hw/m5stopwatch/co5300.c`、
  `hw/m5stopwatch/esp32s3_gpspi.c`、`hw/m5stopwatch/m5sw_i2c_devs.c`、
  `hw/xtensa/meson.build` 等位置失败；
- peripherals `0003` 随后也在同一组共享文件前像失败；
- 因此两组不是可线性串接的公开补丁序列，而是来自不同开发树的历史快照。

### C6 基线

`febae182e132e4055529be423a818225ebddaa3a` 的 GitHub API 返回 `200`。
Issue 中将该 commit 描述为完全不可获取的部分没有复现；正确边界是：C6
adapter 必须应用在 `febae18` 的 C6 machine 树上，而不是普通 9.2.2 tag。

### Release 状态

处理前仓库 releases 数为 `0`。CI 只做 contract/network 测试，不构建 QEMU，
所以 issue 对“CI 绿灯不等于运行时可用”的判断成立。

## 解决

发布 macOS arm64 runtime bundle：

- Release：
  <https://github.com/m5agent/m5stack-esp-emulator/releases/tag/runtime-macos-arm64-2026.10.25>
- Asset：`m5stack-esp-emulator-runtime-macos-arm64-2026.10.25.tar.gz`
- SHA256：
  `735464198c5f7f3ffa930307c0e4cedb973ac48934b73d0092a3a4659831c7a9`
- 大小：`74,636,188` bytes
- Source commit：`10df26ece0b605a3a8bb36a3661b53494fdae9a0`

包内包含：

- self-contained `qemu-system-xtensa`；
- self-contained `qemu-system-riscv32`；
- S3、classic ESP32、C6 ROM；
- `esp-emu 0.50.0`；
- Python 3.13 依赖；
- `INSTALL.md` 和 `RUNTIME-MANIFEST.json`。

文档已更新：

- README 和部署页给出下载、校验、解压和启动命令；
- stopwatch/peripherals 补丁页不再把本地中间 commit 当作公开基线；
- multiboard 与 peripherals 页明确标记为不可线性拼接的历史快照；
- C6 页固定完整公开 commit `febae182e132e4055529be423a818225ebddaa3a`。

## Clean-clone 验证

在全新 public clone `10df26e` 中解压 bundle，使用 Python 3.13 启动
Device Service：

- `sticks3`、`nesso-n1`：`backend_ready=true`、`creatable=true`；
- StickS3 M5Launcher `f1ed15f3...`：135x240 frame，key `a` accepted，
  frame SHA256 `b7c4ffd9...`；
- Nesso N1 Launcher `53a01cdd...`：135x240 frame、4411 非黑像素，
  touch accepted，frame SHA256 `a2736261...`；
- 两个 session 均正常 stopped，历史保留。

首次 StickS3 尝试在已产生非空 frame 后遇到 QMP startup timeout；同固件立即
重试成功。该现象作为 residual service startup flake 保留，不写成 bundle
完全无抖动，也不归因于固件。

## 边界

本交付解决“第三方 clone 后没有可执行 runtime”的直接缺口，但不等于
clean-room source rebuild。源码重建仍需目标分支合并快照或维护者构建流水线。
本 bundle 只支持 macOS arm64 + Python 3.13，不包含 M5Stack 参考固件，也不
提供物理硬件、RF、功耗、声学或电气证据。
