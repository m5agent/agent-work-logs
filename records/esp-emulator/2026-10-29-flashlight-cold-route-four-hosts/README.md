# ESP Emulator FlashLight cold-route four-host validation

- 日期：`2026-10-29`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：`UNIT-HOST-37`
- 源码版本：`m5agent/m5stack-esp-emulator@2bf81aa2814887cdbfa390c9be9a5d23d7e7b96d`
- 环境：macOS Apple Silicon；CoreS3、AtomS3R、StickS3、StopWatch UIFlow2 QEMU；Device Service `/api/v1`

## 结论

原厂 UIFlow2 `FlashLightUnit` constructor 在没有先前高电平边沿的冷启动路径上，
现在会建立可信的 `ready-low`。四台 S3 主机均在同一 guest PID 内依次执行 constructor、
`100% / 220 ms` Flash 和 off Run，状态依次为 `ready-low → flash-active → ready-low`，
未出现 guest reboot。mounted Web consumer 使用同一 CoreS3 session 的实际 QOM 快照回放通过。

结果只覆盖 FlashLight cold constructor、原 100%/220 ms Flash API 和同 PID Run 替换，
属于 `virtual-device validation`。

## 关键证据

- QEMU SHA256：`e318b2b748d6e982cd2e592a1b991ec930a8e9501cf02a0c19925022a656b373`
- CoreS3 / AtomS3R / StickS3 / StopWatch 四台独立 UIFlow-live session 全部 `PASS`
- 每台初始 `output-known/pad-synchronized/gpio-route-supported=true`，`en-level=false`
- 原 API 解码一次 `100% / 220 ms` Flash program；off Run 后重新回到可信低电平
- mounted Web actual-QOM snapshot replay `PASS`；live polling `NOT RUN`
- platform regression：`1559 OK, 10 skipped`
- PR #38 已合并，merge commit：
  `610248e3cc070c6abcf72defc4b3db3048ec77b4`
- PR 两个 run 与 merge commit main run 均为
  `platform-contracts` + `network-namespace-policy` PASS

## 文件

- `report.md`：问题、实现路径、四主机执行与边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：脱敏的四主机与 Web 机器摘要
- `evidence/web-replay.txt`：mounted Unit panel 的 actual-QOM replay 输出

## 未覆盖项

实时 mounted Web 轮询、动态 S1、EN PWM、完整 OEN/IOMUX、bit-exact 时序、
光度、热、电流、电气和 physical hardware 均为 `NOT RUN`。这些结果不能由本次
数字 GPIO/API PASS 继承。
