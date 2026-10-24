# Core2 热门公开固件运行时缺口报告

## 目标

把 public firmware matrix 从 6 台 S3/C6 扩展到 Core2，并对最热门的
M5Burner Core2 官方固件分层判定：

- 结构/partition 是否可导入；
- Device Service 是否真实执行；
- 是否出现非空应用帧；
- 输入是否可观测；
- 串口 panic/PMIC/安全元件错误是否属于固件还是模拟器模型缺口。

## 选择与执行

选择来源为 M5Burner MOST_DOWNLOADED：

1. `UIFlow_Core2`
2. `Core2FactoryTest`
3. `Core2_For_AWS`

执行参数：

- `observe_seconds=90`
- `settle_seconds=5`
- `jobs=1`
- Device Service `/api/v1`
- session 停止使用 `purge=0`

首次 45 秒运行不足以覆盖 Core2 PMIC traceback/MicroPython prompt（约
55–66 秒出现），因此不作为最终结论；随后 90 秒矩阵才是有效窗口。

## 工具超时修复

第一次 90 秒运行仍被错误标成 FAIL。根因是：

- 服务端 `/wait` 允许等待 90 秒；
- matrix client HTTP request 默认也是 90 秒；
- 服务端尚未返回帧条件时，客户端先超时，任务被执行器记为工具错误。

修复：

- `ServiceClient.post()` 增加显式 timeout；
- frame wait 使用 `max(client.timeout, observe_seconds + 15)`；
- 新增 `test_service_client_wait_timeout_tracks_observation_window`。

修复过程中还发现并修正执行函数内误写 `self.timeout` 的未定义变量；最终
`ruff F821` 和 323 项平台测试通过。

## 最终结果

### UIFlow_Core2

- firmware ID `1897200000000002280`
- SHA256
  `18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`
- status `PARTIAL/runtime_model_gap`
- gap `core2_pmic_i2c_model_gap`
- serial 14,003 bytes
- frame nonblack `0`

固件进入 AXP PMIC 初始化并读取寄存器，出现：

```text
hardware/__init__.py ... pmic_axp
OSError: I2C bus error (19)
```

默认 AXP2101 与 `M5SW_CORE2_PMIC=axp192` 都出现该错误。AXP192 运行中
`/machine/axp192` QOM 节点存在，排除了简单设备缺失。

### Core2FactoryTest

- firmware ID `1897200000000000926`
- SHA256
  `4dbddb210d382ed3ca536fc07c962521b238c025016213c947fb4ff7a1bbd4ef`
- status `PARTIAL/runtime_model_gap`
- gap `core2_pmic_i2c_model_gap`
- serial 1,912 bytes
- frame nonblack `0`

日志显示 `M5Core2 initializing...`、I2C 地址扫描和 FT6336 touch 就绪，但
AXP register read 返回 `Error -1`，没有应用帧。

### Core2_For_AWS

- firmware ID `1897200000000000568`
- SHA256
  `22ee8c0f5d3c9640be370cb1a89496ed265b685d573b0e41d62320cf6288ff3a`
- status `PARTIAL/runtime_model_gap`
- gap `core2_aws_atecc608_model_gap`
- serial 9,121 bytes
- frame nonblack `0`

固件启动、LCD 探测和主要时钟初始化后，ATECC608 `atcab_init` 返回 `f0`，
随后 `Core2forAWS` 主动 `abort()`。这不是普通固件崩溃，而是缺少 Core2 for
AWS 安全元件模型。

## 证据层级

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| import | `PASS` | 3/3 公开 image 通过 manifest/partition 分析 |
| execution | `PASS` | 3/3 经真实 Device Service/QEMU session 执行 |
| frame | `FAIL` | 3/3 为黑帧 |
| input | `PARTIAL` | 仅 FactoryTest 有 serial 变化，非应用帧响应 |
| model classification | `PASS` | 3/3 有结构化 runtime model gap |
| hardware | `NOT RUN` | 无物理 PMIC、ATECC608、RF 或电气测量 |

## 影响

- 当前 aggregate public sample coverage 为 7 台设备、21 个样本：
  `10 PASS / 11 PARTIAL / 0 FAIL`。
- Core2 PMIC I2C 与 ATECC608 已登记为 `RUNTIME-03`、`RUNTIME-04`。
- 后续要么补齐模型数据面，要么保持结构化 `runtime_model_gap`；
  不得用 host fake 值把应用黑屏改成 PASS。

## 回滚

回滚 `33d5a28b7be2fb4bbfca6aa96315dcff816530d6` 会移除 Core2 public matrix
分类、runtime env PMIC override 和 wait timeout 修复；历史外部固件不会提交。
