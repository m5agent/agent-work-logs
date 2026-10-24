# 六机型用户固件批量仿真回归报告

## 背景

本记录回答两个问题：

1. M5Burner 热门用户/社区固件能否通过同一 Device Service 路径完成虚拟烧录、
   启动和输入探测；
2. 失败究竟来自固件、服务启动，还是当前 QEMU 模型缺口。

选取策略为 M5Burner `MOST_DOWNLOADED`，排除可替代的 UIFlow2 基线镜像，
每个机型最多 3 个样本。所有样本均通过 `/api/v1/artifacts`、
`/api/v1/firmware`、`/api/v1/sessions`、`/input`、`/frame.png` 和
`/logs` 执行，没有直接启动 QEMU runner，也没有 purge 会话历史。

## 执行

- 18 个 merged firmware 先做结构、chip、flash 和分区检查；
- 每个会话使用独立虚拟 flash；
- 等待非空应用画面；
- 对有屏设备依次发送中间、左中、右中触摸以及 A、Enter 键；
- 对无屏 NanoC6 发送 A、Enter；
- 每次输入后保存 frame 指标与 SHA256；
- 最终读取串口，扫描 assert、panic、WDT、reboot 和错误 chip id；
- 有屏设备只有在 frame + runtime + 至少一个输入响应同时成立时才判 `PASS`。

## 结果

| 设备 | 样本 | PASS | PARTIAL | FAIL | 主要边界 |
| --- | ---: | ---: | ---: | ---: | --- |
| StickS3 | 3 | 3 | 0 | 0 | 物理硬件未验 |
| CoreS3 | 3 | 2 | 1 | 0 | M5Launcher 本次黑屏 |
| Cardputer ADV | 3 | 2 | 1 | 0 | WiFi CSI Radar 无输入响应 |
| StopWatch | 3 | 3 | 0 | 0 | 物理硬件未验 |
| Nesso N1 | 3 | 1 | 2 | 0 | Meshtastic reboot；Bruce 黑屏 |
| NanoC6 | 3 | 0 | 2 | 1 | 无屏；Zigbee WDT |

总计：`PASS 11`、`PARTIAL 6`、`FAIL 1`。

该表是首次 30 秒严格判定基线。后续 45 秒重跑和模型缺口分类将其修正为
当前 `PASS 10`、`PARTIAL 8`、`FAIL 0`；旧结果保留用于比较时序和分类器
演进。

### 非 PASS 明细

- `WiFi CSI Radar ADV + m5 launcher`：应用运行且显示 `No networks.`，但 3 次
  touch 和 2 次 key 均未改变 frame 或 serial，判输入证据不足。
- `M5Launcher for CoreS3 and CoreS3SE`：本次 30 秒窗口内 frame 为 0
  非黑像素；此前单独运行曾出现过非空 frame，当前稳定性不足。
- `NanoC6 Factory Test`、`Evil-NanoC6`：启动、串口和非零按钮输入均执行；
  NanoC6 机型无显示屏，按验收契约保留 `PARTIAL`。
- `Zigbee HA On/Off light For NanoC6`：`Zigbee_main` 未喂 task watchdog，
  每约 2.5 秒重复 WDT。固件包含 IEEE 802.15.4/Zigbee 栈，而当前 C6
  QEMU 没有 802.15.4 radio 数据面；当前分类为
  `runtime_model_gap / PARTIAL`，不是固件 FAIL。
- `Meshtastic unofficial`（Nesso N1）：先渲染 135×240 frame，随后重启并
  报 `Invalid chip id. Expected 13 read 12`。45 秒重跑确认首次已进入 C6
  ROM/application，随后 `LP_SW_HPSYS` 软件复位读回 chip id 12；当前归类为
  `c6_chip_id_lost_after_software_reset / PARTIAL`。
- `Bruce For Arduino Nesso N1`：仅到 ROM/bootloader 早期日志，未形成应用
  画面，也未观察到输入响应。

## 工具改进

本轮修改了矩阵判定器：

- 为每个样本增加 `status_reason` 和 `unmet_requirements`；
- 把 Device Service 启动失败与固件失败分开；
- 无屏机型明确记录为 `serial_only_device`；
- `PASS` 必须包含设备侧可观测输入响应，不能只依赖 HTTP 202/accepted；
- 保存每次输入后的 frame hash。

源码提交：`d0e7abe63bfbaacfc66641a1af0e376252a77f8c`。

## Follow-up：45 秒重跑与 runtime model gap

源码版本：
`m5agent/m5stack-esp-emulator @ e339a6299000656aabbd687b587b949432b642a6`。

对 NanoC6 和 Nesso N1 的 6 个相同 SHA 样本重新执行 45 秒观察窗口：

- 6 个样本全部保持 `PARTIAL`；
- NanoC6 Factory Test / Evil-NanoC6：无屏，serial-only；
- NanoC6 Zigbee：`zigbee_runtime_not_modeled`；
- Nesso Meshtastic：`c6_chip_id_lost_after_software_reset`；
- Nesso Launcher：应用 frame 后出现 `xTaskPriorityDisinherit` assert；
- Nesso Bruce：没有非空应用 frame；
- 原始 serial hash、bounded error lines 和 input 证据继续保留。

分类器新增稳定签名检测：

- `Zigbee_main` + task watchdog → unmodeled C6 Zigbee radio；
- `LP_SW_HPSYS` + `Invalid chip id. Expected 13 read 12` → C6 software-reset
  model defect；
- 一般 `Invalid chip id` 不带软件复位上下文时不会被误归为模型缺口。

合并 18 样本后的当前结果：

- `PASS 10`
- `PARTIAL 8`
- `FAIL 0`
- `runtime_model_gap 2`

验证：

- 平台套件 `316/316 PASS`；
- Node `2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、compileall 和定向
  Ruff：`PASS`；
- GitHub Actions CI run `40075079032`：两个 job 均 `PASS`。

当前结论仍是 FW-03 `PARTIAL`：覆盖 6 台 S3/C6 设备，尚未覆盖全部设备、
ESP32 LX6/P4 和更多 MicroPython/vendor framework。

## 证据

结构化证据：

```text
evidence/verification.summary.json
```

每次运行的 Device Service session ID、firmware/artifact SHA256、
frame SHA256、输入响应和失败签名均记录在该文件中。

## 验证边界

本记录是 virtual-device validation。它不证明：

- 相同固件在实体 M5Stack 设备上的行为；
- Nesso N1 的真实显示旋转/偏移、触摸、LoRa 或 RF；
- NanoC6 的 IEEE 802.15.4/Zigbee 数据面；
- 功耗、声学、光学、机械或长期稳定性。

## 回滚

本轮没有修改或擦除物理设备。源码按提交
`d0e7abe63bfbaacfc66641a1af0e376252a77f8c` 可重新执行用户固件矩阵；
Device Service 会话默认保留历史，flash 副本按正常停止策略释放。
