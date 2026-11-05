# issues #167 / #169 UIFlow2 host-shim 模块覆盖复核报告

## 背景

- 来源：
  - [issue #167](https://github.com/m5agent/m5stack-esp-emulator/issues/167)：AIFlow live
    评测中生成代码 `from umqtt import MQTTClient` 在宿主执行器导入即
    `ModuleNotFoundError: No module named 'umqtt'`，`simulator_draw_calls=0`；
    归因已记为 `evaluation_issue.kind=simulator`、`code=host-stub-module`、
    `module=umqtt`、`non_failing=true`。
  - [issue #169](https://github.com/m5agent/m5stack-esp-emulator/issues/169)：同一
    live 评测的 EPD 代码在宿主执行器出现
    `AttributeError: 'function' object has no attribute 'EPD_QUALITY'`，触发写法
    为官方形式 `M5.Display.setEpdMode(M5.Display.EPDMode.EPD_QUALITY)`；报告者
    同时指出上游文档的 EPD 数值映射可疑。
- 目标：确认这两个 API 是否属于 UIFlow2/host-shim 覆盖范围；在本仓库可用通道
  实际复验；给出外部仓库可落地的修复材料；核对上游文档问题。

## 结论

- 状态：`PARTIAL`。两个 API 的“官方合法 + 在真实固件中可执行”已在本仓库
  `virtual-device validation` 通道复核通过；**外部 host shim 的失败未能复现，
  修复未落地**，因此不能关闭为已修复。
- 关键判断：
  1. `umqtt`、`umqtt.simple`、`umqtt.robust` 是 UIFlow2 官方自带模块，官方
     文档与示例以 `from umqtt import MQTTClient` 为默认写法；`MQTTException`
     只在 `umqtt.simple` 中导出；`umqtt.MQTTClient` 是接受
     `subscribe(topic, handler, qos=0)` 的 M5 包装类。issue 中“最少
     MQTTClient + MQTTException + 几个空实现”的清单不足以支撑该程序形态。
  2. `M5.Display.EPDMode` 是官方 `M5.Display` 成员（`m5unified_gfx.c` 的
     `epd_mode_define_members_table` 与 `mpy_m5gfx.cpp` 绑定），实际常量为
     1..4；非 EPD 面板 `setEpdMode` 静默忽略、`getEpdMode()` 为 0、
     `isEPD()` 为 False；EPD 面板初始化后 `_epd_mode` 已是 `epd_quality`(1)，
     `setEpdMode(0)` 不改变状态，参数必须是 int。
  3. 两个失败组件都是外部 AIFlow eval 仓库的宿主执行器
     (`aiflow_eval/sim_runtime.py`, `engine=uiflow_micropython-host-shim`)；
     本仓库设计上只在 guest MicroPython VM 中执行 UIFlow2 程序（UART raw REPL），
     不在宿主解释 caller Python，因此无法在本仓库合并该修复。
  4. 上游文档 `docs/source/hardware/display.rst:318-328` 的 EPD 数值 `0–3`
     与源码 `1–4` 不一致；知识库副本
     `tools/knowledge-base/uiflow2-coder/docs/hardware/display.md` 同样错误。
     已按内部流程上报 UIFlow2 内部仓库（不公开链接）。
- 改动范围：本工作不修改 m5stack-esp-emulator 任何 tracked 文件；不修改
  UIFlow2 checkout。外部可移植参考补丁与回归测试见 `code/`，由 AIFlow eval
  仓库自行接入。

## 证据

### 官方源码身份（固定 commit）

UIFlow2 源码以 `50e440780492aa847378c7d3477ab912f7063bac`
（`version.txt: Update to V2.5.3.`，与 `release/2.5.3` 的所引文件哈希一致）和
M5GFX 子模块 `9bcedf4e19d4cab7a0793de0598ae5390b4689fe` 为准；逐文件
path/line/sha256 见 [source-provenance.json](evidence/source-provenance.json)。

| 事实 | 位置 | sha256 |
| --- | --- | --- |
| EPD_QUALITY=1 / EPD_TEXT=2 / EPD_FAST=3 / EPD_FASTEST=4 | `m5unified_gfx.c:313-318` | `9e869e68…bac9a4e` |
| `M5.Display` 注册 `EPDMode` | `m5unified_gfx.c:346`（`M5.UserDisplay`:427） | 同上 |
| setEpdMode/getEpdMode/isEPD 绑定 | `mpy_m5gfx.cpp:65-68,121-140`（固定 commit） | `b13f252d…e853f7` |
| EPD 模式枚举与 0 语义 | `M5GFX/src/lgfx/v1/Panel.hpp:79,97-99`、`misc/enum.hpp:42-52` | `fc3850f6…`、`0e8aac59…` |
| EPD panel 初始化写入 quality=1 | `Panel_SSD1677.cpp:188`、`Panel_ED2208.cpp:242` | `c87a4c6a…`、`09517534…` |
| 上游测试使用命名常量 | `tests/display/test_papermono_startup.py:27` | `89223406…` |
| umqtt 三模块 | `m5stack/libs/umqtt/{__init__,simple,robust,manifest}.py` | `5e2eeb76…`、`26da6475…`、`5651475d…`、`c109d13a…` |
| 官方 MQTT 默认导入写法 | `docs/source/software/umqtt.rst:70-79`；`examples/software/mqtt/*.py:8-10` | `283be8f6…`、`0884e95d…` |

### 本轮 fresh guest 执行（virtual-device validation）

隔离的本机 Device Service（agent 自有端口/状态/Token），官方 UIFlow2 设备矩阵
基线，QEMU Xtensa：

| 项目 | issue #169 | issue #167 |
| --- | --- | --- |
| 设备 | PaperMono | CoreS3 |
| 基线固件 SHA256 | `f3da049b65b5a3899d3484594e3bede92a0928e5217fa260925951a777447b05` | `1324f12d3ddd5392f47a9eff537f9ce0b01a8e6e36d829b6bd22cdf82d2c1264` |
| 合成固件 SHA256 | `274ec1576a6513720347048750061c68552f294f474c27b56a1869c2897e8991` | `907f77255a7d5c88ddaa30d6c85410be15e496398d0006d28c3f15e155844d0b` |
| 探针源码 SHA256 | `61ae4a09e9626d6d4d32e555049616a0c131cf3dbca5fe835d8e7638ceca2577` | `76a3be43faa6f831705eb19a82534405aab0cb594c09c133e67a1f10ad721ac5` |
| runtime 二进制 SHA256 | `6d9af027e2f744208fc2503128f1772f436d7ca7358f9e53be597bc76800f39d` | 同左 |
| session | `22df6206f0ab4bafa4fbc85c4cbd9b50` | `fcd5bc0ab22b44468b04cc5238ef8dec` |
| 串口 marker | `ISSUE169_ENUM 1 2 3 4`、`ISSUE169_ISEPD True`、`ISSUE169_MODE_AFTER_BEGIN 1`、`ISSUE169_MODE_AFTER_QUALITY 1`、`ISSUE169_MODE_AFTER_FASTEST 4`、`ISSUE169_MODE_AFTER_ZERO 4`、`ISSUE169_EPD_DONE` | `ISSUE167_MODULES module module module`、`ISSUE167_CLIENT MQTTClient True`、`ISSUE167_SURFACE connect,publish,subscribe,unsubscribe,check_msg,wait_msg,disconnect,ping,isconnected,reconnect,delay,log,set_callback,set_last_will`、`ISSUE167_EXCEPTION_ARGS 5`、`ISSUE167_MQTT_DONE` |
| 帧 SHA256 | `070e8d34628c3bca55bee71fd4db052a7e6535c2525d8a36c30bcfc19436835f` | `57580743a08a3f4ebdf57240cbcc997002ef63b7234531f946127f1495973f43` |
| 清场 | `stopped`、runtime PID gone、history 保留、evidence ZIP `a2dcb02d…` | `stopped`、runtime PID gone、history 保留、evidence ZIP `776a0b89…` |

完整身份、evidence ZIP 与清理字段见
[validation-summary.json](evidence/validation-summary.json)；串口摘录见
[issue169 serial](evidence/serial-issue169-papermono.txt) /
[issue167 serial](evidence/serial-issue167-cores3.txt)。两者均为独立会话、
停止前取 evidence、`purge=0`。

### 参考补丁（外部 eval 仓库）

`code/epd_shim_patch.py`：`EPDMode` 命名空间 + `Screen` 类属性/实例状态/三个
记录式方法；`code/umqtt_host_stub.py`：三模块 stub + `install()` 注册。
宿主单元测试：EPD 26/26、umqtt 9/9 通过，输出见
[host-shim-unit-tests.txt](evidence/host-shim-unit-tests.txt)。这些不是
guest/固件证据，也不表示外部 eval 已修复。

### 执行命令（脱敏）

```bash
# 隔离本地 Device Service（agent 自有端口/状态/Token；不写内网端点）
python3 platform/tools/serve.py <agent-port> --bind <loopback> \
  --state-dir <ignored>/service --api-token-file <ignored>/service.token \
  --max-sessions 2 --max-per-device 2

# guest 探针（复用仓库 tests/uiflow2/api_sweep/run_guest.py；仅绕过其 CLI 设备白名单）
PYTHONPATH=platform/tools:tests/uiflow2 <python> code/run_guest_device_wrapper.py \
  --repo-root <emulator checkout> --api <agent-service-origin> \
  --token-file <ignored>/service.token --device papermono \
  --source code/probe_issue169_epd.py --out-dir <ignored>/run-169 \
  --done-marker ISSUE169_EPD_DONE
# device=cores3 + probe_issue167_mqtt.py + ISSUE167_MQTT_DONE 同理

# 外部 host-shim 参考补丁自测
cd code && python3 epd_shim_patch.py && python3 epdmode_shim_regression_test.py \
  && python3 test_umqtt_host_stub.py
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build（官方源码/文档） | PASS | 固定 commit 的源文件、绑定、文档哈希与行号（`source-provenance.json`） |
| transport（guest UART） | PASS | 两个 session 串口 marker；QEMU runtime 与 PID 身份 |
| device_response（真实固件 API） | PASS | EPD 枚举/状态/`isEPD`；umqtt 导入、方法面、`MQTTException(5)` |
| data_behavior | PASS（限定） | EPD 模式状态机（quality→1、fastest→4、0 忽略）与 umqtt 异常 args 值；未做 MQTT 网络交互 |
| visual_or_physical | NOT RUN | 无物理硬件；未做 RF/光学/电气/机械验证 |
| host-shim 单元测试 | PASS（宿主） | EPD 26/26、umqtt 9/9；仅证明参考实现可移植，不是 guest 证据 |
| 外部 eval 修复 | NOT RUN | 外部仓库不可得；失败未复现、未接入、未复跑 |

## 验证边界

- `aiflow_eval/sim_runtime.py`、`run-171839` 的 `main.py`/traceback 与
  `simulator_draw_calls` 不可得：**失败未复现**；根因机制按报告记录，不额外
  声称已确认 eval 代码现状。
- 未连接任何 MQTT broker、未做 TLS/网络交互；umqtt 结论仅覆盖导入、对象面、
  记录式空实现契约与异常类型，不代表真实 MQTT 会话（既有真实 broker fixture
  证据另见仓库 2026-10-27/28 的 MQTT recipe 记录，本轮未重跑）。
- 未修改 m5stack-esp-emulator tracked 文件、未修改 UIFlow2 checkout；外部
  patch 需由 AIFlow eval 仓库接入后以其自身回归验证。
- 结论仅适用于本轮固定固件/会话身份；不继承到其他固件、设备或物理硬件。

## 风险与回滚

- 无源码仓库改动，无需回滚；隔离 Device Service 与两个 guest 已停止（PID
  消失、history 保留）。
- 外部参考补丁若被接入，需在 eval 仓库以官方写法回归（EPD 命名常量/状态、
  umqtt 三模块导入与调用面）；建议同时把 `umqtt` 加入 host-shim 模块覆盖清单，
  避免同类 `host-stub-module` 失败再次归因到生成代码。
