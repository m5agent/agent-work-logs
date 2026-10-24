# ESP Emulator 运行时模型缺口登记与代码文档重整报告

## 背景

- 来源：用户指出当前代码与文档虽持续更新，但部分页面仍保留既往结论，要求
  完整整理当前已完成工作与待办；
- 目标：以当前 worktree、生成 catalog/profile、最新测试和 evidence JSON 为
  事实源，消除重复、过期和边界混淆；
- 约束：不得把仿真结果写成真机结论；不得把 `runtime_model_gap` 写成固件
  `FAIL` 或模型修复；不得手改生成目录覆盖源 catalog。

## 结论

- 状态：代码、契约、生成档案与文档层 `PASS`；
- 新增统一的运行时模型缺口登记，固定“镜像拒绝、固件失败、模型缺口、
  基础设施错误、未运行”五种分类；
- `RUNTIME-01` 保持 `OPEN`：一个 Nesso N1 Meshtastic 固件执行
  `LP_SW_HPSYS` 后，ROM 报 `Invalid chip id. Expected 13 read 12`；
- `RUNTIME-02` 保持 `OPEN`：NanoC6 Zigbee HA light 依赖尚未建模的 C6
  802.15.4/Zigbee controller；
- Core2 的当前门禁统一为 `5×10s`、`3×60s`、`2×120s`、active-BLE
  `2×120s` 和 3 个独立 lease 各 20 轮 reconnect；
- C6/Core2 的源 catalog、QEMU profile 和生成后的设备档案已同步。

## 文档漂移与修复

| 页面/数据 | 旧状态 | 修复后 |
| --- | --- | --- |
| `unified_core2` 专题 | 十轮 reconnect | 二十轮 reconnect，并保留十轮/五轮/双轮历史证据 |
| `core2_openeth` 夹具 | 说 Core2 WiFi 仍 `PARTIAL` | 明确 OpenETH 只是独立 Ethernet 夹具，不否定后续 OpenMAC WiFi PASS |
| StickS3 外设 | IMU accel/gyro 为零 | `0.250/-0.500/0.750` 与 `10/-20/30` 经 UIFlow2 API PASS |
| Core2 catalog/profile | 缺 120 秒、active-BLE 和二十轮结果 | 与当前 evidence 和 30 轮 API 上限对齐 |
| C6 catalog/profile | 只写基线 PASS | 额外列出 `RUNTIME-01`/`RUNTIME-02` 两个 OPEN blocker |
| 文档导航 | 未区分模型缺口 | 新增缺口登记、固件 evidence 索引和新鲜度条目 |

文档契约测试还增加了防回归门禁：缺口代码必须与跨厂商 evidence、当前状态、
Backlog、工作流和缺口登记同时一致；旧 WiFi/IMU/十轮/core panic 表述不得回到
当前入口。

## 执行

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
Ran 317 tests in 12.847s
OK

node platform/tests/test_sha256.mjs
SHA256_OK

node platform/tests/test_firmware_upload.mjs
FIRMWARE_UPLOAD_OK

python3 platform/tools/runtime_coverage.py --check
RUNTIME_COVERAGE_OK

python3 platform/tools/peripheral_catalog.py --check
PERIPHERAL_CATALOG_OK

python3 platform/tools/qemu_profiles.py --check
QEMU_PROFILES_OK

python3 -m json.tool <catalog/profile files>
PASS

git diff --check
PASS
```

GitHub Actions `40075831017`：

```text
platform-contracts        success
network-namespace-policy  success
```

## 当前工作与待办

| 工作流 | 当前状态 | 下一道门禁 |
| --- | --- | --- |
| 网络 | namespace、DNS/TLS allowlist、exact IPv4 egress、pcap、错误密码、radio/AP 恢复、DHCP renewal、双 guest fabric、worker mTLS/rotation/QEMU reattach | `NET-04` 跨主机 executor/companion continuity；`NET-05` IPv6 |
| Core2 | native-HCI `HCI-1` 至 `HCI-4`、extended hold、二十轮 reconnect PASS | `CORE2-02` >20 轮、多小时 soak/coexistence、controller/baseband、物理 cache/PSRAM |
| 通用固件 | Manifest、WebBurner、静态审查、安全配置、文件系统、18 样本矩阵 | `RUNTIME-01`、`RUNTIME-02`、`FW-01`、`FW-03`、`FW-02` |
| Device Service | lease、queue、worker、mTLS、rotation、reattach、GC | `SVC-01` 自动化迁移/continuity、`SVC-02` warm pool、`SVC-03` 编排拆分 |
| 专项后端 | Tab5 partial；CardputerZero 独立 Linux 后端 | `TAB5-01`、`CZ-01`、`UI-01` |
| 真机 | 无同固件 SHA 记录 | `HW-01` |

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | 317 个平台测试、Node 2/2、Python compile、CI |
| review | `PASS` | catalog/profile/生成档案/链接/陈旧结论/缺口对应关系 |
| transport | `NOT RUN` | 本次未启动新设备会话 |
| device_response | `NOT RUN` | 本次没有修改或重跑 QEMU 数据面 |
| data_behavior | `NOT RUN` | C6 reset/controller 缺口仍未修复 |
| visual_or_physical | `NOT RUN` | 无 UI、RF、功耗、声学或机械测量 |
| hardware | `NOT RUN` | 未操作物理设备 |
| delivery | `PASS` | 源码提交、CI、工作记录与双远端发布 |

## 验证边界

- 本次的 PASS 只覆盖代码/契约/生成档案/文档一致性和既有 evidence 的对账；
- `RUNTIME-01` 的真实 chip-id 读取来源仍未定位；
- `RUNTIME-02` 是否可实现、需要多少工作量仍未评估完成；
- 没有重跑完整 67-case QEMU 矩阵，因为本次没有修改 QEMU controller 或
  device probe；
- 没有任何物理硬件、RF、功耗、声学、光学或电气结论。

## 风险与回滚

- 风险集中在 blocker 元数据和文档门禁；现有 `/api/v1`、QEMU 二进制和用户
  会话未被修改；
- 回滚源码提交：
  `git revert d6694295e1ebee48f1056c2894171c48da6cac99`；
- 回滚不会修复或改变两个 C6 模型缺口，它们仍应按 `runtime_model_gap`
  返回。
