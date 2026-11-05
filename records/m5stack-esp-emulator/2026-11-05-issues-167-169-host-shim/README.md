# M5Stack Emulator GitHub issues #167 / #169：UIFlow2 host-shim 模块覆盖复核

- 日期：`2026-11-05`（Asia/Shanghai）
- 结果：`PARTIAL`
- 工作类型：`issue`
- 问题来源：[issue #167](https://github.com/m5agent/m5stack-esp-emulator/issues/167)、[issue #169](https://github.com/m5agent/m5stack-esp-emulator/issues/169)
- 源码版本：[m5stack-esp-emulator @ 082fffafd124800564d11c82b56cc4ecbb2c503d](https://github.com/m5agent/m5stack-esp-emulator/tree/082fffafd124800564d11c82b56cc4ecbb2c503d)
- 环境：macOS arm64、隔离的本机 Device Service（agent 自有端口/状态/Token）、官方 UIFlow2 固件的 QEMU Xtensa guest；未使用物理硬件

## 结论

两个 issue 都是 **外部 AIFlow eval 仓库宿主执行器（`aiflow_eval/sim_runtime.py`，
`engine=uiflow_micropython-host-shim`）的模块/API 覆盖缺口**，不是生成代码、
模型能力或本模拟器 guest 执行失败：

- `umqtt` / `umqtt.simple` / `umqtt.robust` 属于 UIFlow2 官方 API 面，官方源码与
  文档明确把 `from umqtt import MQTTClient` 作为默认写法；
- `M5.Display.EPDMode` 是官方 `M5.Display` 成员，四个常量实际值为
  `EPD_QUALITY=1 / EPD_TEXT=2 / EPD_FAST=3 / EPD_FASTEST=4`，上游测试同样使用
  命名常量写法；
- 两个 API 都在本仓库的 `virtual-device validation` 通道中于同一天重新执行通过：
  PaperMono guest 打印 `ISSUE169_ENUM 1 2 3 4`、`ISEPD True`、
  `MODE_AFTER_BEGIN 1`、`AFTER_QUALITY 1`、`AFTER_FASTEST 4`、`AFTER_ZERO 4`；
  CoreS3 guest 完成 `from umqtt import MQTTClient` 导入、方法面核对和
  `MQTTException(5)`，串口 marker 见下。

本记录**不声称 eval 已修复**：`aiflow_eval/sim_runtime.py` 不在本工作区，失败
无法在这里复现，参考补丁只能由外部 eval 仓库接入并以它自己的回归验证。两个
GitHub issue 保持 open，等待外部仓库落地修复；本记录作为公开证据入口。

同时确认了 issue #169 指出的上游文档数值错误：`docs/source/hardware/display.rst`
把 EPD 模式写作 `0–3`，与源码 `1–4` 不一致（示例 `Display.setEpdMode(2)`
实际解析为 `EPD_TEXT`）。该问题已按内部流程向 UIFlow2 内部仓库报告。

## 关键证据

- 构建或运行：官方 UIFlow2 固件基线
  `f3da049b65b5a3899d3484594e3bede92a0928e5217fa260925951a777447b05`（PaperMono）与
  `1324f12d3ddd5392f47a9eff537f9ce0b01a8e6e36d829b6bd22cdf82d2c1264`（CoreS3）；
  合成固件 `274ec157…e8991` / `907f7725…4d0b`；QEMU 二进制
  `6d9af027e2f744208fc2503128f1772f436d7ca7358f9e53be597bc76800f39d`。
- 实机或服务执行：两个可见 Device Service session
  `22df6206f0ab4bafa4fbc85c4cbd9b50`（PaperMono）与
  `fcd5bc0ab22b44468b04cc5238ef8dec`（CoreS3）；均为 evidence-before-stop、
  `purge=0`，guest PID 消失、history 保留。
- 日志、测量或协议：串口 marker 见
  [issue169](evidence/serial-issue169-papermono.txt) /
  [issue167](evidence/serial-issue167-cores3.txt)；完整身份见
  [validation-summary.json](evidence/validation-summary.json)；帧 SHA256
  `070e8d34…6835f`（PaperMono）与 `57580743…973f43`（CoreS3）。
- 源码与仓库证据：官方 UIFlow2 `50e44078…`（内容与 `release/2.5.3` 一致）及
  M5GFX `9bcedf4e…` 的逐文件 SHA256、本仓库 API 清单与 R8 全 19 板验收身份见
  [source-provenance.json](evidence/source-provenance.json)。
- issue 回复（2026-11-05，均含本记录固定提交链接）：
  [#167 comment](https://github.com/m5agent/m5stack-esp-emulator/issues/167#issuecomment-6649047956)、
  [#169 comment](https://github.com/m5agent/m5stack-esp-emulator/issues/169#issuecomment-6649047482)。
- 参考补丁：EPD 26/26 项、umqtt 9/9 项宿主单元测试通过，见
  [host-shim-unit-tests.txt](evidence/host-shim-unit-tests.txt)；代码见
  [code/](code/README.md)。

## 文件

- [report.md](report.md)：背景、逐 issue 复核、执行路径、证据、边界与回滚。
- [run.json](run.json)：机器可读记录（issue、固件/运行时/会话身份、checks）。
- `evidence/`：脱敏串口 marker、验证摘要、源码 provenance、单元测试输出。
- `code/`：guest 探针、设备包装器、外部 host-shim 参考补丁与回归测试。
- `patches/`：不适用——外部 `aiflow_eval/sim_runtime.py` 源码不在本工作区，
  无法生成可按 base commit 应用的最小 patch；参考实现见 `code/`。

## 未覆盖项

- 外部 AIFlow eval 仓库的 `sim_runtime.py` 与 `run-171839` 原始产物不可得：
  报错栈、`simulator_draw_calls` 等失败细节**未复现**，只按 issue 记录理解。
- 未在外部 eval 仓库执行接入、集成或 case 复跑；本记录的补丁是参考实现，
  不代表 eval 已经修复。
- 物理硬件、RF、功耗、光学、电气和机械属性：`NOT RUN`；本记录全部结论属于
  `virtual-device validation`。
- 未新跑 browser-WASM 通道；本轮 fresh guest 验证走原生 QEMU Device Service。
- 第三方 MQTT broker、TLS 或真实网络交互：`NOT RUN`（umqtt 探针只验证导入/
  对象面/异常，不建立 socket）。
