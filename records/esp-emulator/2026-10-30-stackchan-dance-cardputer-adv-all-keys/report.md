# ESP Emulator StackChan 跳舞固件舵机与 Cardputer-ADV 全键复核报告

## 背景

- 来源：用户反馈完整 StackChan 跳舞固件在浏览器模拟器中仍停在
  `左右 0.0° / 抬头 45.0°`，同时要求确认 Cardputer-ADV 每个按键是否对应真实键位。
- StackChan 固件：完整 Flash SHA
  `c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542`，
  对应源码 SHA
  `7ee22ca570acd7f105d8205b3bc67ecc19e60ce11b1533f3481fc1288081bb9e`。
- Cardputer-ADV：锁定 M5Cardputer `bf64d317`、M5Unified `0.2.28`、
  M5GFX `0.2.35` 重建的 8 MiB 完整 Flash。
- 目标：证明同一用户固件路径中的舵机数据面确实变化，并逐键验证真实键盘矩阵，
  不用抽样或代码阅读代替执行。

## 结论

### StackChan

根因位于浏览器 QEMU 的执行调度，不在固件角度逻辑、SCS 帧格式、UART 路由、
QOM 输出或 DOM 状态展示。

默认 1:1 虚拟时钟下，用户固件的 M5GFX 首帧在 TCG/WASM 中约需 2.2 秒；
跳舞固件 cue 间隔为 400 ms。网页时间线每轮先吸掉多个 cue，再重置运动插值
起点，因此长期没有机会进入位置插值写循环。最小 UART/SCS 固件和最小绘图探针
分别通过，排除了总线、广播 `SYNC_WRITE`、QOM 和网页消费问题。

修复为 app-bound profile：仅当完整 Flash SHA 精确匹配时，StackChan 使用
`stackchan-wasm-dance-div6`。同一探针的真实 6:1 虚拟时钟把首帧缩短到约
300 ms。官方参考固件与其他固件仍保持 `stackchan-wasm-wallclock`，不继承
这份兼容选择。

### Cardputer-ADV

原实现让浏览器输入、CAD component 名和真实 TCA8418 行列分散在多个局部映射
中，修饰键和继承自桌面键盘的旧 component 名容易漂移。此次新增 canonical
表，同时保存：

- 物理 4×14 布局和真实键帽字面；
- TCA8418 7×8 行列与 event；
- CAD component 名与逻辑 QKeyCode；
- Browser `KeyboardEvent.code` 和左右修饰键别名。

实际测试通过原厂 `M5Cardputer.update()` 与 TCA8418 GPIO11 IRQ reader，
不是只检查映射对象。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | source-built QEMU WASM 固定为 `5d6c36...a993`；Cardputer 合同固件按锁定依赖重建 |
| flash | PASS（virtual-device） | 两个完整 Flash 由各自 browser QEMU session 启动；启动 marker 与完整帧可观察 |
| transport | PASS（virtual-device） | UART1 SCSCL、真实 TCA8418 IRQ、PC keyboard event 到 switch 的路径均执行 |
| device_response | PASS（virtual-device） | `rejected_packets=0`；56 个物理键均产生按下、位置和释放 |
| data_behavior | PASS（virtual-device） | yaw `307..613`、pitch `677..850`；Cardputer 36/36 checks |
| visual_or_physical | PASS（virtual） / NOT RUN（physical） | 1056 个 StackChan 帧、Cardputer 四旋转/局部像素/纹理通过；机械和光学未测 |
| delivery | PARTIAL | PR #65 同一 head 两项 CI 各 2/2 PASS，但 PR 仍 OPEN、未合并 |

### StackChan 数据面

- profile：`stackchan-wasm-dance-div6`，clock divisor `6`；
- 30 个有效 SCS 包，`rejected_packets=0`；
- yaw present/goal：`307..613`；
- pitch present/goal：`677..850`；
- 23 个状态样本、1056 个真实帧；
- 3D 关节跟随 present position，DOM ticks 与角度标签消费同一 snapshot；
- 串口保持原固件初始化与 cue 序列；
- 正常 Stop 后 engine 与 5 个嵌套 pthread target 全部关闭。

### Cardputer-ADV 全键

- 56/56 个物理键匹配原厂 reader 的按下位置与释放；
- 55 个直接 PC code 到达各自真实物理开关；
- 左右 Shift、Ctrl、Meta、Alt 别名通过；
- 双 Shift 同时持有、分别释放和大小写路径通过；
- `Escape`、`Delete`、四方向键的固件组合键路径通过；
- 四旋转、四角、局部 64 像素和原生纹理绑定通过；
- 同一 guest 无 page error，正常 Stop 后 Worker target 为 0。

容易误配的旧 CAD 名称现已显式固定：

- `key-Escape` 是物理 grave/Fn-Escape；
- `key-CapsLock` 是物理左 Shift；
- `key-AltLeft` 是 Opt/Meta，`key-AltRight` 是 Alt；
- `key-Quote` 是 apostrophe，`key-Period` 是 dot；
- PC `MetaLeft/MetaRight` 路由到物理 Opt；
- PC `ShiftRight` 路由到物理 Shift，`ControlRight` 路由到物理 Ctrl；
- `Delete` 是 Fn + Backspace，箭头键是对应 Fn chord；
- PC `CapsLock` 故意不映射，因为 Cardputer-ADV 没有该物理键。

## 执行与证据

- 平台回归：

```bash
PYTHONPATH=platform/tools \
  /tmp/esp-emulator-py312/bin/python3.12 \
  -m unittest discover -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
```

- 结果：platform 1,725 项，`OK (skipped=10)`；四个生成器/合同检查 PASS。
- 逐键与浏览器合同：
  `test_cardputer_keymap.mjs`、`test_model_shell.mjs`、
  `test_public_qemu_profiles.mjs`、`test_stackchan_dance_user_firmware.mjs`
  与 `test_public_qemu_cardputer_input_display.mjs` PASS。
- PR head：
  `6db2b817506fade96fde45e5984aa46b1c7876ed`。
- 同一 head 的两次 CI：
  [41039534961](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41039534961)、
  [41039285653](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41039285653)，
  两项 job 均 PASS。

## 旧记录修正

2026-10-29 StackChan 记录保留的派生摘要曾写有 `1006` 个 SCS
`SYNC_WRITE` 包，但公开记录没有保留可重算此数字的原始 SCS trace。
该计数现降级为“历史上报值，未独立复核”，不再作为当前可验证事实。此次
exact-SHA browser test 在不同运行窗口直接观测 30 个有效包和真实位置变化，
不能用来反推或替换旧 native 96 秒窗口的 1006。

## 验证边界

- 两个结果都是 `virtual-device validation`，不是物理硬件验证。
- div6 是慢速虚拟设备兼容路径，不证明墙钟、机械实时性、PWM 或电气时序。
- 未验证 StackChan 实体舵机是否接受广播扭矩/位置写、机械零位、堵转、电流、
  噪声和寿命。
- 未验证 Cardputer-ADV 实体键帽手感、LCD 光学方向、背光和键盘电气抖动。
- 只覆盖列出的 firmware、WASM、manifest 与 profile SHA。

## 风险与回滚

- 本次没有修改用户 StackChan 跳舞固件，也没有提交固件、ROM 或 raw execution artifact。
- 需要回滚时整体 revert PR 对应提交；profile 只匹配一个完整 Flash SHA，不匹配时
  自动保持原 wallclock 路径。
- Cardputer-ADV 映射改动只影响该设备；若实体键盘出现与模型/reader 不同的硬件事实，
  应先停止对外确认并重新核对官方矩阵，再修订 canonical 表。
