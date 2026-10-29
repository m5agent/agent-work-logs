# M5Stack ESP Emulator SVC-03 device-spec boundary 报告

## 背景

- 来源：`SVC-03` Device Service 编排热区拆分。
- 目标：把设备目录、matrix/profile 和设备后端选择从
  `device_service.py` 移到无会话状态模块。
- 约束：不改变对外 symbol、错误、HTTP、session/evidence 或 QEMU 参数。

## 结论

- 状态：`PASS`。
- 新模块：`platform/tools/device_service_specs.py`。
- 移动范围：
  - `DeviceSpec`
  - `load_device_specs`
  - matrix/profile/catalog paths
  - QEMU backend path 和 ROM override
  - Core2 radio QEMU selection
  - network/runtime profile constants
- `device_service.py` 保留 same-object re-export。

## 验证

```text
device-spec tests:       5/5 PASS
Device Service tests:  125/125 PASS
QEMU profile tests:     20/20 PASS
platform full suite: 1604 run, 1603 PASS + 1 skip
docs contracts:         50/50 PASS
```

runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
compileall、Ruff `E9/F` 和 diff check 均 PASS。

SVC-03 的下一门禁是继续提取剩余请求解析和运行参数构造，再拆
store/runtime/evidence/session。本次没有移动这些边界。

## 验证边界

该变更没有修改 QEMU controller、firmware、网络策略或硬件路径，因此没有
用一次重构替代现有 runtime PASS。物理硬件、RF 和电气验证
`NOT RUN/不变`。

## 风险与回滚

主要风险是遗漏模块级路径或 profile constant 的旧调用方。same-object
re-export、public symbol identity、14-device catalog 和完整平台测试覆盖该
边界。回滚为 revert `823dd890`。
