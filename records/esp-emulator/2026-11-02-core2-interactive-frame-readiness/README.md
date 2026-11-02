# ESP Emulator Core2 interactive blank-start readiness

- 日期：`2026-11-02`
- 结果：`PASS`（virtual-device；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 问题来源：用户要求复测 `m5core2_voronoi v1.0.3` 在 Core2 QEMU 中
  `ready_timeout` 的原因
- 源码版本：`m5agent/m5stack-esp-emulator @ b4d066cf`，修复提交 `6b45ec86`，
  PR [#78](https://github.com/m5agent/m5stack-esp-emulator/pull/78) 合并为
  `b6b8d6fe`
- 固件：公开项目
  [`cubic9com/m5core2_voronoi v1.0.3`](https://github.com/cubic9com/m5core2_voronoi/tree/v1.0.3)
- 环境：macOS、Core2 QEMU `m5core2`、Device Service、虚拟 `320x240` ILI9342
  framebuffer 与触摸输入

## 结论

固件和模拟器数据面均正常。该应用故意以黑色 canvas 启动，只有收到第一次触摸后才绘制；
旧自动矩阵同时要求 PNG 至少 `1024` 字节，导致压缩后仅 `602-615` 字节、但全部
`76,800` 个像素均非黑的合法画面被误判为未就绪。

修复后保留像素级非黑断言，只把 PNG 传输字节数的下限降为 `1`。同一固件的中心触摸和
拖动均被接受并改变画面，最终审核路径从 `FAIL/E_SIM_APP_NOT_READY` 收敛为
`done/SIM_VERIFIED`，耗时约 `21.8 s`。

## 关键证据

- 输入前：有效 PNG、`0/76,800` 非黑像素；
- 中心触摸：输入接受，frame SHA 从 `57580743…` 变为 `94d84a52…`；
- 拖动：输入接受，frame SHA 从 `94d84a52…` 变为 `a52cbcac…`；
- 最终帧：`320x240`、`76,800/76,800` 非黑像素、`2` 个唯一颜色；
- 自动矩阵测试：`28/28 PASS`；
- PR #78 head `4/4` CI 通过；合并后 main CI 的 platform-contracts 与
  network-namespace-policy 两个 job 均通过；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：根因、修复、执行和边界
- `run.json`：结构化记录
- `evidence/summary.json`：固件、会话、像素指标和输入证据摘要
- `evidence/frame-after-touch.png`：第一次触摸后的 framebuffer
- `evidence/frame-after-drag.png`：拖动后的最终 framebuffer
- `patches/`：不适用；最小修复为 PR #78 的一行阈值改动
- `code/`：复现使用仓库内 `platform/tools/user_firmware_matrix.py`

## 未覆盖项

- 未在物理 Core2 上执行本应用；物理触摸、LCD 光学和供电行为均为 `NOT RUN`。
- 本结论只覆盖同一公开固件 SHA 的 virtual-device 路径，不外推到其他固件版本。
- 恶意软件/木马检测为 `NOT RUN`；静态字符串检查不能替代动态安全检测。
