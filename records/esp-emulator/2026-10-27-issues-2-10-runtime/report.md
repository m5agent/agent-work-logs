# ESP Emulator GitHub issues #2–#10 顺序复测报告

## 背景

- 来源：公开仓库 `m5agent/m5stack-esp-emulator` 的 issues #2–#10。
- 需求：在刚合并的最新模拟器上依次复测；未解决的问题尝试修复；确定解决的
  issue 可以关闭。
- 基线：`8a0d99a03e3205564011bb123e0ee981587bebe7`。
- 最终主线：`a0ad8150b112afe1273100514c7ef0808bd4477b`。

## 结论

本轮整体为 `PARTIAL`：

| Issue | 结论 | 处理 |
| --- | --- | --- |
| #2 Core2 四 app 无首帧 | `FAIL`，仍复现 WDT/reset 与 302-byte 纯黑 frame | 保持 open |
| #3 Core2 NTP/Wi-Fi 前无内容 | `FAIL`，仍复现 WDT/reset 与 302-byte 纯黑 frame | 保持 open |
| #4 ENV III / QMP6988 | `PASS`，既有主线修复有效 | 关闭 |
| #5 Servo8 HAT | `PASS`，scan `[54]`、angle `90`、power `1` | 关闭 |
| #6 CoreS3 8Servos | `PASS`，Port A `[64]`、Port B `[37]`、mode `3`、angle `90` | 关闭 |
| #7 CoreS3 Joystick2 | `PASS`，scan `[99,100]`、B `(1200,-800)`、button `True` | 关闭 |
| #8 CoreS3 NFC | `PASS`，scan `[80]`、detect `DEADBEEF` | 关闭 |
| #9 Cardputer ADC calibration | `PASS`，calibration applied、无 fatal、nonblank/running | 关闭 |
| #10 Cardputer Tetris setup stall | `PASS`（限定 setup 路径），显示 `ALL SETUP OK` | 关闭并写明逻辑边界 |

## 根因与改动

### Unit I2C 控制器

`0048-unit-servos8-joystick2-nfc.patch` 在真实 guest I2C 控制器之后添加：

- StickS3 Hat2-Bus `servo8-hat@0x36`；
- CoreS3 Port B `8servos@0x25`；
- Joystick2 `0x63`/`0x64`，包括创建期地址选择与冲突检查；
- ST25R3916 NFC `0x50`，复用确定性 fixture，并暴露 transaction/byte/UID 计数。

专用端口不在通用 Unit catalog 中扩大准入。端口 registry 使用
`admitted_unit_ids` 将 Hat2-Bus 限定为 `servo8-hat`，将 CoreS3 Port B
限定为 `8servos`；其它 Unit 以 `unit_port_not_supported` 拒绝。该限制来自
CI 发现的首版回归：只改 `physical_presence` 会把其它已准入 I2C Unit
意外放宽到未验证端口。

### Cardputer-ADV ADC

新增 app-bound synthetic calibration fixture。Service 仅对 Cardputer-ADV、
`qemu-esp32s3` 且 application segment 匹配的镜像，写入 17 个白名单
ADC calibration/version eFuse 字段；identity/security 字段不变。无论是否
用 Unit，evidence ZIP 都包含 `units/adc-calibration.json`。

### 未解决项

#2/#3 的失败点在 Core2 legacy runtime，而不是本轮 Unit/ADC 改动。最终
runtime 仍出现 `Interrupt wdt timeout`、`TG1WDT_SYS_RESET` 等 marker；
当前 frame 为 320×240、302-byte、nonblack 0、一种颜色。没有把这些 reset
误判为 Python 异常或测试通过。

## 执行环境

- macOS arm64；
- Python `3.12.14`；
- Node.js 与锁定 browser dependencies；
- QEMU `esp-develop-9.2.2-20260417`，
  commit `40edccac415693c5130f91c01d84176ae6008566`；
- 14 patches / 109 source files；
- runtime SHA256
  `9aca9a8db5143ad133510795cd228ed8ac23c388ea197267d7b2b4750e58eb82`；
- source receipt SHA256
  `1219a45d8ad495509e01088f87af5fe7e41719bb4661e6e60afc42fdce035b26`。

所有功能执行使用 Device Service `/api/v1` 可见 session。每个 session 先
请求 evidence ZIP，再停止并设置 `purge=0`，保留 metadata、日志和最后 frame。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | cold build、source receipt、14-patch replay、`0048` reverse-check |
| transport | `PASS` | 原 UIFlow2 I2C scan、controller transaction counters |
| device_response | `PASS` | ENV/Servo/Joystick/NFC 原驱动返回；Cardputer app 启动 |
| data_behavior | `PASS` | QOM 值随 session inputs 与 guest writes 变化 |
| visual_or_physical | `PASS`（virtual visual） | #4–#10 nonblank frame；#2/#3 纯黑失败保留 |
| review | `PASS` | 代码差异、端口准入与证据脱敏审阅 |
| delivery | `PASS` | PR #13 两 jobs 全绿后合并 |
| physical_hardware | `NOT RUN` | 本轮只使用经验证的虚拟设备路径 |
| full_uiflow2_matrix | `NOT RUN` | 不属于本次 issue 最小回归边界 |

本地门禁：

```text
platform tests: 1241 PASS, 1 skipped
runtime coverage: PASS
peripheral catalog: PASS
QEMU profiles: PASS
project snapshot: PASS
Unit runtime: 18 PASS
Unit ADC fixture: 17 PASS
Unit controller patch: 2 PASS
offline Unit fault controls: PASS
Node Unit/browser contracts: PASS
PR scope: 35 new blobs / 1,737,075 bytes / evidence 24,955 bytes
```

GitHub CI：

- [runs 40448991510 / 40448995266](https://github.com/m5agent/m5stack-esp-emulator/pull/13/checks)
  的 platform-contracts 与 network-namespace-policy 均为 `PASS`。

## 证据索引

完整值、session ID、firmware SHA、串口 marker、frame SHA 和 evidence ZIP
SHA 见 [evidence/summary.json](evidence/summary.json)。

最终 frame：

- `evidence/frames/issue2.png`
- `evidence/frames/issue3.png`
- `evidence/frames/issue4.png`
- `evidence/frames/issue5.png`
- `evidence/frames/issue6.png`
- `evidence/frames/issue7.png`
- `evidence/frames/issue8.png`
- `evidence/frames/issue9.png`
- `evidence/frames/issue10.png`

原始 evidence ZIP 未直接发布，因为 Service manifest 中含唯一 device code。
记录保留 ZIP SHA256、字节/成员摘要结论和相关数据面值，不公开设备唯一标识。
PNG 无 metadata，未发现敏感字段。

## 验证边界

- #2/#3 仍为 `FAIL`，不关闭。
- #4 是既有主线修复复验，不是本 PR 新引入。
- #5/#6 不证明真实舵机运动、电流、电源开关、ADC 输入或电气限制。
- #7 不证明机械行程、中心、方向或模拟量校准。
- #8 不证明 RF field、天线、距离、真实卡片或 secure-card 行为。
- #9/#10 不证明电池 ADC 精度或物理电气特性。
- #10 原始 Tetris 完整源码缺失；只覆盖 issue 的 setup 路径。

## 风险与回滚

所有功能 session 已停止，Flash 未保留；历史 session、串口和末帧保留。
物理设备没有写入或改动。源码回滚可 revert
`a0ad8150b112afe1273100514c7ef0808bd4477b`；QEMU patch 栈以项目内
`0048` 和 source receipt 固定。
