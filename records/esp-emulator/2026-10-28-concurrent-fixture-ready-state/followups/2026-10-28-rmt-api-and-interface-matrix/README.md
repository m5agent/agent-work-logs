# ESP Emulator 三设备 UIFlow2 接口矩阵与 RMT API 夹具

- 日期：`2026-10-28`
- 结果：`PARTIAL`（接口矩阵与 RMT API 路径 PASS；stock 固件、模型和物理边界保留）
- 工作类型：`code_change` + `virtual_device_validation`
- 问题来源：用户要求并发复测 StopWatch、StickS3、Core2 的 UIFlow2 接口，并统一处理失败
- 源码版本：`m5stack-esp-emulator @ 90f556387560a47230141946e96f6f0166266721`
- 相关实现：`014eb6dcb2be2588f19a94c4257e37e5583a5c21`
- 环境：macOS arm64、Device Service `/api/v1`、QEMU TCG virtual device、
  UIFlow2 `v2.5.3`；物理硬件未使用

## 结论

三台设备以“设备间并发、设备内有序”方式完成 system runtime、shared
corrections、完整设备组、通信协议、ESP-NOW、UI 与输入复测。发现并补齐一个
Device Service 接口缺口：矩阵已使用 `M5SW_RMT_TX_FILE`、
`M5SW_RMT_RX_FILE` 和 `M5SW_RMT_TRACE`，但 trusted-local `runtime_env`
白名单未放行，导致 StickS3 IR 无法经 `/api/v1` 验证。补齐后 IR TX/RX
均在可见 session 中 PASS，RMT symbols 解码回 NEC `0x56/0xA3`。

StopWatch、StickS3、Core2 的设备组分别为 `6/6`、`5/5`、`6/6`。
Core2 IMU 在设备组通过后另行完成 `3/3` 独立首跑，加上组内首跑共 `4/4`。
三台 UI smoke 均收到真实输入 marker，最终帧成功标记为绿色。

原厂 frozen firmware 的 `requests2.urlencode`、Modbus async
`Loop.sock_recv` 和 TLS epoch 失败仍是固件源码缺陷；前两项的 hash-pinned
candidate 本轮重新通过。它们不由模拟器 PASS 覆盖。

## 关键证据

- QEMU SHA256：
  `6ff2aca091909ea078e5b9805b420cb04c11e3f9928b52c2fac199e33e45b2ef`
- StopWatch firmware：
  `99d6482befe094de47bf68ce43618d3868bd62fb1fc72f0b55c0d0c2ea4e7f8d`
- StickS3 firmware：
  `c08196024019273ccadee9b4b3da303567f7ab206fa14edd1af283f04f6e98d8`
- Core2 firmware：
  `b228c0e2d877e77a8a352e917ed84f4da8ea92d15b25e28f431a2999620fe3c4`
- 设备组：StopWatch `6/6`、StickS3 `5/5`、Core2 `6/6`，无 retry
- Core2 IMU：组内 `1/1` + 独立 `3/3`
- UI smoke：`466x466`、`135x240`、`320x240`；输入 marker PASS，
  成功像素分别为 `(233,233)`、`(3,3)`、`(2,2)`，RGB `(0,255,0)`
- RMT IR TX/RX：两个独立 `/api/v1` session PASS
- 全平台测试：`1364` 项 `OK`，`1` skip

## 文件

- [report.md](report.md)：执行矩阵、失败分类、修复和边界
- [run.json](run.json)：机器可读记录
- [evidence/summary.json](evidence/summary.json)：脱敏后的计数与哈希

## 未覆盖项

- 物理硬件、触控压力、显示光学时序、声音、RF 和电气验证；
- 外部/PMK 加密 ESP-NOW peer 与跨设备 fabric；
- Core2 legacy `RUNTIME-03` 原厂 startup UI、normal-WDT、setup/REPL
  和完整应用帧；
- Core2 完整 28 类 M5UI 文档方法矩阵。
