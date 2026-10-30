# ESP Emulator StackChan 跳舞固件舵机与 Cardputer-ADV 全键复核

- 日期：`2026-10-30`
- 结果：`PASS`（virtual-device）；交付 `PARTIAL`（PR #65 已合并；后续页面与门禁见 follow-up）；物理硬件 `NOT RUN`
- 工作类型：`code_change`
- 问题来源：[PR #65](https://github.com/m5agent/m5stack-esp-emulator/pull/65)
- 源码版本：`m5agent/m5stack-esp-emulator@6db2b817506fade96fde45e5984aa46b1c7876ed`
- Base：`f6bcab037c813892626f61edb2900920dcf9199e`
- 环境：macOS arm64；Chromium `156.0.8078.74`；browser QEMU WASM；StackChan 与 Cardputer-ADV 虚拟设备

## 结论

StackChan 不动不是跳舞固件锁角，也不是 SCSCL 帧或网页 QOM 消费错误。默认
1:1 浏览器 QEMU 下，该固件首帧在 TCG/WASM 中约耗时 2.2 秒，而舞蹈 cue
间隔只有 400 ms；每轮时间线更新会一次跨过多个 cue、重置插值起点，导致没有
进入持续位置写入。修复只把完整 Flash SHA
`c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542`
绑定到 `stackchan-wasm-dance-div6`，官方参考固件和其他固件仍使用原 profile。
同一 guest 随后观测到真实位置变化：左右 `307..613`、抬头 `677..850`。

Cardputer-ADV 的 4×14 逻辑键盘与真实 TCA8418 7×8 矩阵已收敛到一张 canonical
映射表。同一完整 Flash 通过原厂 `M5Cardputer.update()` / TCA8418 GPIO11 IRQ
reader 验证了 `56/56` 个物理键的按下、位置和松开；55 个可直接对应的 PC code
全部到达真实开关，左右修饰键、Esc/Delete 和四个方向键 chord 也已逐项通过。

## 关键证据

- StackChan Flash：
  `c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542`。
- QEMU WASM：
  `5d6c36bdafc1129c2652b5ba9422f3deb5ab170475748cea96fdc4cf9520a993`。
- 最终本地导出 manifest：
  `c27de9d6cc7230829d368b82fbf23a9f0cc39146dc716cab1e1eefd05f17b985`。
- StackChan：30 个有效 SCS 包、`rejected_packets=0`、23 个状态样本、
  1056 个真实帧；3D 关节、DOM ticks 和角度标签消费同一 position snapshot。
- Cardputer-ADV Flash：
  `4faaccde28367c257f7f140c139c434cf223be47de41ad853a168d9c25c2bd7b`。
- Cardputer-ADV：36/36 checks，56/56 物理键，55/55 direct PC codes，四旋转和
  局部像素/纹理绑定通过。
- 本地 platform suite：1,725 项，`OK (skipped=10)`；profile、coverage、
  peripheral catalog 和 project snapshot 检查通过。
- PR head CI：
  [run 41039534961](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41039534961)
  与
  [run 41039285653](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41039285653)
  对同一 head 均为 2/2 job PASS。
- 两个正常 Stop 都关闭 engine 与 5 个嵌套 pthread target，最终 worker 数为 0。

## 文件

- `report.md`：根因、修复、逐项验证和边界。
- `run.json`：结构化记录。
- `evidence/summary.json`：脱敏后的机器可读证据摘要。

## 未覆盖项

- 物理 StackChan、实体舵机机械行程、扭矩、电流、供电和长期稳定性 `NOT RUN`。
- 物理 Cardputer-ADV 键盘、键帽手感、LCD 光学方向和电气时序 `NOT RUN`。
- `stackchan-wasm-dance-div6` 是慢速兼容路径，不是物理实时性能或等价时序证明。
- 结果只覆盖记录的 firmware、WASM、manifest 和 profile；其他 SHA 不继承 PASS。
- PR #65 已合并；正式页面更新与 regular all-admitted 剩余边界见
  [`followups/2026-10-30-pages-production`](followups/2026-10-30-pages-production/)。
