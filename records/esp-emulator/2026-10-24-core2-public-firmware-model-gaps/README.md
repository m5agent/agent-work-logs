# ESP Emulator Core2 热门公开固件与模型缺口

- 日期：`2026-10-24`
- 结果：`PARTIAL`
- 工作类型：`runtime_model_gap`
- 源码提交：`m5agent/m5stack-esp-emulator @ 33d5a28b7be2fb4bbfca6aa96315dcff816530d6`
- 环境：macOS Apple Silicon；QEMU `m5core2`；Device Service `/api/v1`

## 结论

通过 M5Burner MOST_DOWNLOADED 选出的 3 个 Core2 官方固件均在 90 秒窗口内
执行。结果为：

- `0 PASS`
- `3 PARTIAL`
- `0 FAIL`
- `3` 个应用帧非黑像素为 `0`
- `3` 个结构化 `runtime_model_gap`

| 固件 | 当前结果 | 模型缺口 |
| --- | --- | --- |
| `UIFlow_Core2` `1897200000000002280` | `PARTIAL` | AXP PMIC 寄存器读取返回 I2C error |
| `Core2FactoryTest` `1897200000000000926` | `PARTIAL` | AXP PMIC 寄存器读取返回 I2C error |
| `Core2_For_AWS` `1897200000000000568` | `PARTIAL` | ATECC608 安全元件未建模，初始化失败后 abort |

`UIFlow_Core2` 还做了默认 AXP2101 与
`M5SW_CORE2_PMIC=axp192` 的 A/B；两者都出现同一
`OSError: I2C bus error (19)` 和黑帧，因此不能写成固件单方面失败。

## 工具修复

90 秒运行暴露了 matrix client 的 HTTP 超时误杀：服务端 `/wait` 被允许等待
90 秒，但客户端请求也只用 90 秒，长窗口因此被记为 FAIL。修复后 wait timeout
使用 `observe_seconds + 15`，并新增回归测试。修复前的短窗口和客户端超时
快照均保留为失败历史，不参与最终 status。

## 关键证据

- 平台测试：`323/323 PASS`
- Node：`2/2 PASS`
- CI run `40089720526`：两个 job 均 `PASS`
- 当前组合样本覆盖：7 台设备、21 个公开非基线固件
- 组合结果：`10 PASS / 11 PARTIAL / 0 FAIL`

## 文件

- `report.md`：样本选择、执行、I2C/A-B、ATECC608 与工具修复
- `run.json`：机器可读记录
- `evidence/verification.summary.json`：artifact hash、结果和缺口

## 未覆盖项

- 未证明物理 Core2/Core2 for AWS PMIC、ATECC608、RF 或电气行为；
- 未实现 AXP PMIC 事务或 ATECC608 模型；
- 未重跑完整 UIFlow2 67-case 外设矩阵。
