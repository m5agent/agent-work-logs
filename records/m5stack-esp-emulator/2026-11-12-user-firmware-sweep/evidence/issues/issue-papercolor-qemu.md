## 现象

2026-11-12 批量矩阵中，PaperColor 官方厂测固件 **PaperColor_Factory_Code** 在 Device Service（`runtime=qemu`）上运行时，QEMU 进程以 **SIGABRT（exit code -6）** 退出，会话被记为 `failed`，取证中断。

出现时机不固定：崩溃那轮在会话创建后约 **8.7 s** 发生；同一固件的另外几轮可正常运行 68–75 s。故为**间歇性 host 端断言**。

固件信息：

- M5Burner firmware_id：`1897200000000000148`
- SHA-256：`a3f5ca4ae89dd724dd8f9b2d800fd9749af84bf0cf2fffbf99cdf822b285f419`
- 设备：`papercolor`（ESP32-S3，8 MiB PSRAM，400×600 EPD）

## 复现

崩溃会话：`3dfc8a33aba34f6586982a86fda05a9c`（`created_at 13:30:16Z`，`completed_at 13:30:25Z`，`error: process exited with code -6`）。

`qemu.stderr` 全文：

```
Adding SPI flash device
**
ERROR:../accel/tcg/cputlb.c:1845:atomic_mmu_lookup: code should not be reached
```

运行路径：agent 自有 Device Service `18787` + `platform/tools/serve.py`，`M5_QEMU_XTENSA=.work/local-runtime-sync-20261111/native/qemu-system-xtensa`，仓库提交 `1506de25`；固件经 `POST /api/v1/artifacts` → `/firmware`（merged）→ `/firmware/analyze`（valid）→ `/sessions` 创建。

复现次数：独立 6 次运行（68 s / 8.7 s / 75 s / 75 s / 75 s / 75 s）中 **1 次**崩溃。

## 影响

- host 进程崩溃会直接毁掉该会话的串口/帧证据，并让批次中断；对“先跑矩阵再判读”的批量回归是不可恢复的失败。
- `atomic_mmu_lookup` 是 QEMU TCG 的 host 侧断言，理论上不应由 guest 行为触发；无论根因是 PSRAM/cache、SOC 模型还是固件异常，都不该以 host abort 收场。

## 期望 / 验收

1. 用同一固件 SHA 在 PaperColor 上复跑，抓到可重复的触发条件（若需并发/时序，记录具体条件）。
2. 把该路径修成 guest 级错误（MMU/cache 访问失败应产生 guest 异常或会话错误），而不是 host 断言。
3. 加一个最小回归（同一故障注入或同固件）验证：会话以 `failed/stopped` 正常收尾，`qemu.stderr` 不再出现 `cputlb.c ... atomic_mmu_lookup`。

## 附：同固件另有可稳定复现的 USB 缺口

同轮矩阵里该固件还稳定打印 TinyUSB 初始化失败（与应用不中断运行）：

```
check_dwc2 183: ASSERT FAILED
dwc2_core_init 221: ASSERT FAILED
...
E (2404) tinyusb_task: Init TinyUSB stack failed
```

这属于 PaperColor 板级 USB OTG（device 模式）未建模，和上面的 host abort 是两个独立问题；如需要我另开一条 issue 跟踪。

## 边界

- virtual-device 验证；未使用真机，不涉及功耗/电气/光学结论。
- 未修改固件、flash 或设备 profile。
