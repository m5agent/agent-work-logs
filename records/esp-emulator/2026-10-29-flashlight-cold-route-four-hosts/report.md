# ESP Emulator FlashLight cold-route four-host validation 报告

## 背景

- 来源：`UNIT-HOST-37`，后续由 PR
  [#38](https://github.com/m5agent/m5stack-esp-emulator/pull/38) 收口。
- 现象：原厂 constructor 只把 EN 配置为低电平，没有先产生高→低边沿时，旧模型保留
  `output-known=false`，因此无法区分“确认熄灭”和“状态未知”。
- 目标：使用真实 GPIO/IOMUX/OE/RTC 来源建立无边沿冷低基线，并在多个 S3 host 上用
  原厂 UIFlow2 源码路径验证 constructor、Flash API 与 Run 替换。

## 结论

- 状态：`PASS`（virtual-device validation）
- 根因：controller-derived output state 在无先前边沿时未形成可信低电平；host 不能把
  一个低 pad 读数直接当作模型内部状态证据。
- 改动范围：`0047-unit-flashlight-cold-pad-observation.patch` 在 controller pad 层记录
  route、IOMUX、OE、RTC 和外部/偏置来源；新增可重放的
  `tests/units/run_flashlight_route_probe.py`，并让 mounted Web 测试消费同一 session 的
  实际 QOM 快照。
- 兼容：历史 FlashLight OUT_SEL 路由修复 `0046` 保持；本次没有扩展该结论到动态 S1、
  PWM 或电气模型。

## 证据

### 代码或配置

```text
UIFlow2 guest:
  FlashLightUnit((white, yellow))       -> FLASHLIGHT_CONSTRUCTOR_LOW
  flash(BRIGHTNESS_100, TIME_220MS, False)
  flash(0, TIME_220MS, True)

Observed state:
  initial      ready-low, output-known=true, decoded-programs=0
  after Flash  en-level=true, 100%, 220ms, decoded-programs=1
  after off    ready-low, output-known=true
```

### 执行

- 环境：macOS Apple Silicon；QEMU `e318b2b7…`；Device Service `/api/v1`
- CoreS3 firmware：
  `0ede40601c1e37b7ba32c87a3ca55e4da7a448f6cf52957f005763bc7c7c78e8`
- AtomS3R firmware：
  `0c70da2a56102dc812f380ac24fcb0a75bd3cb0c70e5380d97c11baeca935323`
- StickS3 firmware：
  `93a547011be37a2b5f062ad7a56da108a95600119d360481adef10c634ed8d76`
- StopWatch firmware：
  `869f8a192cbc0392c8905cf69cfa7244482e97221cce977a04e9dc191f46ff21`
- 每台主机创建独立 UIFlow-live session，挂接 U152 Flash fixture，按上述三个程序替换
  执行；停止前请求 evidence ZIP，并以 `purge=0` 停止。
- 四台均保持同一 PID，串口 reboot banner 数量没有增加。
- mounted Web 用 CoreS3 自 initial/active/off 的实际 QOM 属性通过真实 UnitPanel；
  该测试不启动新的 guest，也不等于实时轮询。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | QEMU profile、patch 组合与项目快照检查 |
| transport | PASS | Device Service HTTP、UIFlow-live source submission、串口 marker |
| device_response | PASS | QOM `output-known`、route/pad synchronization、Flash program metadata |
| data_behavior | PASS | 四 host 的 `ready-low → flash-active → ready-low`、同 PID、无 reboot |
| visual_or_physical | NOT RUN | QOM 状态与 mounted replay 不是光度、热、电流、电气或真机测量 |

平台回归为 `1559 tests OK, 10 skipped`；runtime coverage、peripheral catalog、
QEMU profiles、project snapshot 和 mounted Web replay 均 PASS。PR #38 的两次检查
和 merge commit main CI 也通过。

## 验证边界

本次只关闭 `UNIT-HOST-37` 的 cold constructor/低基线数字边界。实时 mounted Web
轮询、动态 S1、EN PWM、完整 OEN/IOMUX、bit-exact timing、光度、热、电流、电气和
physical hardware 都未验证。其他 Unit 可以复用 controller 状态机制，但不能继承本页
PASS，仍须各自执行对应 guest/主机路径。

## 风险与回滚

改动没有修改公共 Unit 字段；mounted Web replay 只消费已有实际 QOM 属性。回滚 PR #38
会移除四主机 probe、Web snapshot replay 和当前状态记录，但不会恢复旧的
`output-known=false` 行为，因为 controller 修复来自已合入的 `0047`。异常 guest 路径
通过停止 session、释放 QEMU 和 `purge=0` 清理；硬件没有写入或烧录。
