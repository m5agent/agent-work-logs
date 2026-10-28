# StopWatch / StickS3 / Core2 UIFlow2 三设备接口复测报告

## 背景

- 来源：用户要求在三个当前 UIFlow2 目标上并发复测接口，收集失败后统一处理共性问题。
- 目标：区分固件缺陷、模拟器模型边界、证据 oracle 不足和通过项，避免仅凭 import/return code 记 PASS。
- 输入：M5Burner UIFlow2 v2.5.3 基础镜像、项目当前 28-patch QEMU runtime 和 hash-pinned SDK 候选源码。

## 结论

- 状态：`PARTIAL`。
- 稳定通过的域：system runtime、sockets、MQTT、网络、EasySocket、EzData，以及候选 HTTP form encoding 和
  candidate Modbus 全路径。
- 已定位并修复的共享缺陷：requests2 URL 编码、BLE UUID32、Modbus frame transform、Modbus async socket、
  M5UI Canvas/Image/Spinbox marshalling。
- 仍存在但未在本轮关闭的边界：StopWatch drawPixel、QR/TLS 候选固件重建、WAV/mic 数据面、
  ESP-NOW payload 路由、Core2 callback 稳定性和部分 UI oracle。

## 环境

| 项目 | 值 |
| --- | --- |
| validation | `virtual-device validation` |
| physical hardware | `NOT RUN` |
| UIFlow2 | `v2.5.3` |
| QEMU | `40edccac415693c5130f91c01d84176ae6008566` |
| runtime SHA256 | `21b7e34cc96560b4c8185131791008ae49fb1c6975a8428e4e344188a8236394` |
| StopWatch firmware | `ef5e81b6da17ba04a0356b3bde782e9f0f8f93b217701a4414a52a8d8d8532c0` |
| StickS3 firmware | `c45d4514e21d94a6c069185e08f05851c75b4747d354c1423decdefa625e1dd3` |
| Core2 firmware | `b228c0e2d877e77a8a352e917ed84f4da8ea92d15b25e28f431a2999620fe3c4` |

测试使用独立可见 Device Service session。每个 session 先请求 evidence ZIP，再以 `purge=0` 停止；
最终确认 QEMU PID 消失、Flash 释放，测试服务停止。原始 serial/frame/ZIP 留在临时工作缓存，不进入公开记录。

## 验证结果

| 域 | StopWatch | StickS3 | Core2 |
| --- | ---: | ---: | ---: |
| system runtime | 51/51 | 51/51 | 51/51 |
| shared SDK candidates | 7/7 | 7/7 | 7/7 |
| sockets | 23/23 | 23/23 | 23/23 |
| MQTT | 42/42 | 42/42 | 42/42 |
| network | 14/14 | 14/14 | 14/14 |
| HTTP stock | 15 PASS / 1 FAIL | 15 PASS / 1 FAIL | 15 PASS / 1 FAIL |
| HTTP candidate | 2/2 | 2/2 | 2/2 |
| EasySocket | 57 PASS + 1 N/A | 57 PASS + 1 N/A | 57 PASS + 1 N/A |
| Modbus stock | 42 PASS / 8 ERROR | 42 PASS / 8 ERROR | 42 PASS / 8 ERROR |
| Modbus candidate | 50/50 | 50/50 | 50/50 |
| EzData owned fixture | 17/17 | 17/17 | 17/17 |
| ESP-NOW control plane | 8 PASS + 5 STATE_PASS + 1 configured | 同左 | 同左 |

`system runtime` 的 51 项包含一个显式板级边界 `STATE_PASS`。ESP-NOW send/recv/IRQ 稳定归类为
`BLOCKED_MODEL`，不把控制面配置成功外推为无线 payload PASS。

## 根因与修复

### requests2 URL encoding

stock `urlencode` 未正确转义保留字符和 UTF-8。候选 `0002` 在 StopWatch、StickS3、Core2 上各 `2/2`
通过。

### BLE 32-bit advertising UUID

两个 BLE advertising decoder 都把 4-byte UUID 当成 8-byte `double` 解包，stock 三台均报
`buffer too small`。候选 `0021` 直接把原始 4-byte payload 交给 `bluetooth.UUID`；16/32-bit 向量通过。

### Modbus TCP→RTU frame

`transform_frame` 先构造 `func_code=0` 的非法 RTU frame，导致 stock 失败。候选 `0022` 从 TCP fields
直接构造 RTU frame，request/response/exception 的 RTU bytes 和 CRC 均通过。

### Modbus async socket

八个 async TCP 方法调用 MicroPython 不存在的 `Loop.sock_recv`。候选 `0023` 在 MicroPython 分支使用有界
`select.poll` + `socket.recv`，保留 CPython 原路径；三台 Modbus 均达到 `50/50`。

### M5UI native marshalling

Canvas triangle descriptor 点数组未回写；Core2 M5Image 单参数 float scale 触发 float→int 错误；
Core2 整数 Spinbox step 被乘十。候选 `0001` 在 StopWatch/Core2 stock→candidate 同 VM 对照中通过。
StopWatch 最终有效 oracle 为 `4 STATE_PASS + 2 FRAME_PASS`。

## M5UI 与显示

- StopWatch 的 28 个 M5UI 类均可构造；505 项文档方法批次中 409 `STATE_PASS`，剩余主要是画面/输入/删除
  oracle、无 recipe 和一项明确 unsupported。
- Core2 的 28 类均可构造；已完成 90 项文档方法样本，其余 22 类的完整方法矩阵仍为 `REVIEW`。
- StickS3 当前镜像不导出 `m5ui`/`lvgl`，分类为 `NOT_EXPORTED`。
- StopWatch `drawPixel` trace 只有 CASET/RASET/RAMWR 头，没有像素数据；单像素宽度与 CO5300/AMOLED
  偶数窗口限制冲突，仍为固件/绑定缺陷。
- 文本 glyph 因没有 OCR oracle，不把 `drawString` 返回成功当作视觉 PASS。

## 协议与硬件模型边界

- TLS stock 三台均在 mTLS handshake 报证书有效期过期；已有 epoch 候选 patch 未重建本轮候选固件。
- `Widgets.QRCode.setText` stock 仍显示旧 QR；已有源码 patch 未重建候选固件验证。
- StopWatch/StickS3 在 `playWav` 后调用 `playWavFile` 不返回；Core2 可完成。
- 三台 Mic API 可返回，但无 PCM 输入时 buffer 为零；StopWatch/StickS3 recording state 保持为 1。
- ESP-NOW 实例、配置和 peer table 可用；OpenMAC 缺少 vendor-action peer TX/RX route，payload/IRQ 阻塞。
- Core2 PWR callback 只保留一次通过记录；BtnA hold callback 不稳定，当前为 `REVIEW`。

## 回归

```text
PYTHONPATH=platform/tools:.work/py python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
Ran 1344 tests in 106.391s
OK (skipped=1)

python3 platform/tools/runtime_coverage.py --check       -> RUNTIME_COVERAGE_OK
python3 platform/tools/peripheral_catalog.py --check     -> PERIPHERAL_CATALOG_OK
python3 platform/tools/qemu_profiles.py --check          -> QEMU_PROFILES_OK
python3 platform/tools/project_snapshot.py --check       -> PROJECT_SNAPSHOT_OK
docs index/current-state contracts                        -> 20/20 PASS
git diff --check                                         -> PASS
```

## 验证边界

本记录不证明物理硬件、RF、天线、声学、光学、功耗或电气行为。源码候选结论只适用于记录的 firmware/runtime
hash 和上传源码；不能写成原厂冻结固件已经修复。QR/TLS 需要重建对应候选固件后补测，WAV/mic 和
ESP-NOW 需要补齐模型数据面，Core2 UI/callback 需要继续扩大重复运行样本。

## 风险与回滚

候选 patch 都是窄范围 Python 源码修正。回滚只需撤销对应 patch；不影响已有基础固件或 QEMU runtime。
虚拟 session 在停止时默认释放 mutable Flash，未执行不可逆物理烧录或安全配置变更。
