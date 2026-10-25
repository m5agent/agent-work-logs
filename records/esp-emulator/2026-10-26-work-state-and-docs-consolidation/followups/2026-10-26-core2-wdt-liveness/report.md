# Core2 WDT liveness report

## 背景

上一轮 `0039/0040` 证明 cache handoff 在首次 reset 前完成约 4,376 次，排除了
“单次 handoff 永不返回”。上一份当前状态仍把下一门禁描述为“首个 stage-0
timeout 后 feed/service 为何不恢复”。本轮直接验证该前提。

## 执行

新增的 `run_wdt_liveness.py`：

- 每次使用独立 Device Service 和 QEMU lease；
- 不启用 `M5SW_XTENSA_PC_TRACE`；
- 启用统一 handoff trace 和 TIMG verbose trace；
- 运行 18 虚拟秒；
- 保存 serial、frame、QEMU stderr 哈希和 session SHA；
- 解析 TG0 stage-0/stage-1、TG1 feed 间隔、timeout 和 reset 顺序。

固件为 public `UIFlow_Core2 v1.15.4`，normalized SHA
`152127c808b9212e3a5b55dd9e0a2d24e71b902e225452b67db381c76caba1cc`。
QEMU SHA 为
`f7ac5a0352eb4345f5c3b719a5dd656c5c0cdfb3d805cf258f144d1ae1fb6718`。

## 三次结果

| run | TG0 stage-0 | TG0 stage-1 reset | TG1 feeds | max TG1 interval | last feed to reset |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `5.910698 s` | `15.912522 s` | 6,681 | `8.505 ms` | `1.797 ms` |
| 2 | `5.922631 s` | `15.926661 s` | 6,618 | `10.410 ms` | `4.271 ms` |
| 3 | `5.910705 s` | `15.912004 s` | 6,807 | `8.478 ms` | `1.779 ms` |

三次 TG0 stage-0 中断均被 mask，stage-0 后没有 TG0 feed/reconfigure/protect
写入。TG1 在每轮都无 timeout，并持续 feed 到 reset 前数毫秒。

Serial 均只有 MicroPython banner、无 REPL。frame 均为 302-byte PNG，SHA256
`57580743a08a3f4ebdf57240cbcc997002ef63b7234531f946127f1495973f43`。

## 结论修正

当前配置下不成立的前提：

- “TG1 已停止 feed”；
- “首 reset 是 TG1 interrupt-WDT”；
- “最后固定 800 ms 是当前必然路径”。

当前分类是：

`BOOTLOADER_TG0_STAGE1_RESET_WITH_TG1_LIVE`

历史 `800 ms` TG1 gap 被保留为特定 trace 配置下的日期化证据，并在三次
无 PC trace 对照中标记 `NOT_REPRODUCED`。

下一门禁：按启动 phase 拆分 TG0 stage-1 前的 guest/controller 工作，解释
该检查点当时看到的启动进度问题。后续 45/120 秒 WDT-off late-state 将边界
推进到约 44 秒后的 CPU1 `0x40100049` flag/object wait；该 follow-up 取代
本条中的下一门禁描述，但不修改三次 liveness 的原始结果。

## 验证

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、Ruff `E9/F`、Node SHA/upload |
| virtual-device data behavior | `PASS` | 三次独立 WDT liveness 运行、无失败 |
| generated contracts | `PASS` | runtime coverage、peripheral catalog、QEMU profiles、project snapshot |
| platform regression | `PASS` | 平台 `520/520`；定向 `59/59` |
| delivery | `PASS` | product commit `b074640`；CI `40241669357` 两个 job 均 PASS |
| legacy application | `FAIL` | banner-only、无 REPL、black frame、TG0 stage-1 reset |
| full UIFlow2 matrix | `NOT RUN` | 本轮没有重跑 67 cases |
| physical hardware | `NOT RUN` | 无真机、物理 watchdog、RF 或电气测量 |

## 验证边界

- 所有功能结果都是 `virtual-device validation`；
- TIMG verbose trace 开启，因此不声称运行路径零扰动；
- TG1 feed live 不等于 TG1 驱动路径或真实 controller timing 正确；
- 黑色 frame 和 TG0 stage-1 reset 仍代表 legacy 应用启动失败；
- 该记录不关闭 `RUNTIME-03`。

## 风险与回滚

没有烧录、擦除或持久设备修改。runner 只使用 Device Service 临时 lease，
结束时以 `purge=0` 保留历史并停止服务。回滚 product commit
`b07464052a915780e014a12fe6b3ad0f016d8162` 可恢复上一状态。retained QEMU
worktree 不得 reset/clean。
