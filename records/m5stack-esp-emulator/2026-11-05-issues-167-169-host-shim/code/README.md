# code — 可重建的验证程序与参考补丁

这些文件不是 m5stack-esp-emulator 仓库的一部分：本仓库在 guest MicroPython VM
中执行 UIFlow2 程序，不提供宿主 Python 执行器。`aiflow_eval/sim_runtime.py`
属于外部 AIFlow eval 仓库，本记录只提交可直接移植的参考实现与回归测试。

## guest 验证程序（在真实 UIFlow2 固件中执行）

| 文件 | 用途 |
| --- | --- |
| `probe_issue169_epd.py` | 在 PaperMono UIFlow2 固件中执行官方写法 `M5.Display.setEpdMode(M5.Display.EPDMode.EPD_* )`，打印枚举值、`isEPD()`、`getEpdMode()` 状态与 `setEpdMode(0)` 语义 |
| `probe_issue167_mqtt.py` | 在 CoreS3 UIFlow2 固件中执行 `from umqtt import MQTTClient` / `from umqtt.simple import MQTTException`，枚举客户端方法面并触发 `MQTTException(5)` |
| `run_guest_device_wrapper.py` | 调用仓库既有 `tests/uiflow2/api_sweep/run_guest.py` 的 `run()`；仅绕过其 CLI 设备白名单，镜像合成、可见 Device Service session、停止前取 evidence ZIP、`purge=0` 均为原实现 |

运行方式（隔离服务使用 agent 自有端口与状态目录；不写内网端点）：

```bash
# 1) 启动 agent 自有的本地 Device Service（独立端口/状态/Token）
# 2) 以 guest 方式运行探针
PYTHONPATH=platform/tools:tests/uiflow2 \
  <python> records/.../code/run_guest_device_wrapper.py \
  --repo-root <emulator checkout> \
  --api <agent-owned service origin> \
  --token-file <agent-owned token file> \
  --device papermono \
  --source records/.../code/probe_issue169_epd.py \
  --out-dir <new ignored dir> \
  --done-marker ISSUE169_EPD_DONE
```

`--device cores3` + `probe_issue167_mqtt.py` 同理（done marker 为
`ISSUE167_MQTT_DONE`）。实际执行身份和串口 marker 见
[`../evidence/validation-summary.json`](../evidence/validation-summary.json)。

## 宿主 shim 参考补丁与回归（外部仓库可移植）

| 文件 | 用途 |
| --- | --- |
| `epd_shim_patch.py` | issue #169 的最小参考补丁：`EPDMode` 命名空间（1..4）、`Screen.EPDMode` 类属性以绕过 `__getattr__` 函数回落、`isEPD()/setEpdMode()/getEpdMode()` 记录式实现、非 EPD 语义、int 校验；并自测 |
| `epdmode_shim_regression_test.py` | 26 项宿主单元测试：官方写法的属性链、四个常量、状态机、`setEpdMode(0)` 忽略、非 EPD no-op、类型拒绝和动态 API 回落保留 |
| `umqtt_host_stub.py` | issue #167 的单文件三模块 stub：`umqtt` / `umqtt.simple` / `umqtt.robust`，匹配冻结官方签名；所有网络动作为可记录 no-op；提供 `install()` 与 recorder/scheduler hook |
| `test_umqtt_host_stub.py` | 9 项宿主单元测试：导入面、客户端方法面、M5 wrapper 的 `subscribe(topic, handler)` 分发、录制序列、无 socket 断言和 UIFlow2 程序启动形态 |

运行：

```bash
cd records/<this-record>/code
python3 epd_shim_patch.py                 # EPD_HOST_SHIM_PATCH_PASS
python3 epdmode_shim_regression_test.py   # 26/26 checks passed
python3 test_umqtt_host_stub.py           # 9/9 PASS
```

这些是 **host-shim 单元测试**，不是 guest/固件证据，也不代表外部 eval 已修复。
