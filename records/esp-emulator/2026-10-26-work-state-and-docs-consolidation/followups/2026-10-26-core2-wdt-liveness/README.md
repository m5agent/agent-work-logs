# Core2 WDT stage and feed-liveness reconciliation

- 日期：`2026-10-26`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ b074640](https://github.com/m5agent/m5stack-esp-emulator/commit/b07464052a915780e014a12fe6b3ad0f016d8162)
- Base commit：`e420570ebdfe89dae75612938fbe80281c5413ef`
- 环境：macOS `26.5.1` arm64；Python `3.13.15`；QEMU 9.2.2 virtual Core2；
  physical hardware `NOT RUN`

## 结论

新增 `run_wdt_liveness.py`，在三个独立 Device Service lease 中关闭 PC trace、
启用 TIMG verbose trace。三次运行得到一致分类：

`BOOTLOADER_TG0_STAGE1_RESET_WITH_TG1_LIVE`

- TG0 stage-0 timeout 在约 `5.91 s` 发生，但 WDT 中断被 mask；
- 首次 reset 来自 TG0 stage-1，在约 `15.91 s` 发生；
- TG1 每轮完成 `6,618-6,807` 次 feed；
- TG1 最大相邻 feed 间隔为 `8.478-10.410 ms`；
- TG1 最后一次 feed 距 reset 仅 `1.779-4.271 ms`；
- 三次运行均为 `0` 次 TG1 interrupt-WDT；
- TG0 stage-0 后没有 feed、reconfigure 或 protect 写入。

早期 `800 ms` TG1 gap 没有删除，而是保留为特定 trace 配置下的历史观测，
在当前无 PC trace 的配置中标记为 `NOT_REPRODUCED`。因此当前首要问题改为：
legacy 应用初始化为什么没有在 TG0 stage-1 deadline 前完成。

同一固件仍只有 MicroPython banner、无 REPL、302-byte black frame，所以
`RUNTIME-03` 继续为 `OPEN`。

后续 45/120 秒 WDT-off late-state 对照进一步把边界收敛到约 44 秒后的
CPU1 `0x40100049` flag/object wait，并替代本条中的“应用初始化为何未在
stage-1 deadline 前完成”作为当前下一步。见
[后续记录](../2026-10-26-core2-wdt-off-late-state/)；本条三次 liveness
evidence 保持不改写。

## 关键证据

- runner SHA256：
  `49e06c42f750935d4e468827f14ecf5872013581c552ddb39383627a626ba25a`
- evidence SHA256：
  `1061d950225c0fb3a4876b07b6c503a7f5dab9f00f3af8e347940358c68585cd`
- contract SHA256：
  `a8586bf915f776ab9b3f13696b61d865933a6c7d8c561b96077053c4bb52fe8f`
- normalized public firmware SHA256：
  `152127c808b9212e3a5b55dd9e0a2d24e71b902e225452b67db381c76caba1cc`
- QEMU binary SHA256：
  `f7ac5a0352eb4345f5c3b719a5dd656c5c0cdfb3d805cf258f144d1ae1fb6718`
- platform tests：`520/520 PASS`
- focused Core2/docs/profile tests：`59/59 PASS`
- product CI：run `40241669357` 的 `platform-contracts` 与
  `network-namespace-policy` 均 `PASS`

## 文件

- `report.md`：实现、三次运行、文档修正、验证和边界；
- `run.json`：机器可读结果；
- `evidence/core2-wdt-liveness-summary.json`：三次 WDT 状态；
- `evidence/verification.summary.json`：测试、生成物和 CI 汇总。

## 未覆盖项

- TG0 stage-1 前的具体 firmware startup phase 仍未定位；
- 没有 matching `UIFlow_Core2 v1.15.4` ELF/MAP；
- `0039/0040` 后没有重跑完整 UIFlow2 67-case 矩阵；
- 仍无 REPL、非空应用帧或 stable guest；
- 所有结果都是 `virtual-device validation`，不是物理 watchdog、RF、cache
  timing、功耗、电气或真机结论。
