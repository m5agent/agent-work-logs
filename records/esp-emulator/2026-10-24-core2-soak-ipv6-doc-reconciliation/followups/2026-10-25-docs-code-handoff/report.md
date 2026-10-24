# ESP Emulator 当前状态、代码边界与执行队列重整报告

## 背景

- 来源：用户要求完整整理代码与文档，并把近期 Core2、网络、公开固件和
  Device Service 工作合并到当前状态。
- 现象：文档数量较多，部分页面仍写旧 API 上限、旧 RSS 归因状态和历史样本
  计数，容易把“接口允许”“历史 SHA 结果”和“当前制品功能验证”混为同一层。
- 目标：建立一个无内部矛盾的当前入口，明确已完成、在途、待执行、模型缺口
  和真机边界，并增加自动化防回归。

## 结论

- 状态：`PASS`（仅指本轮 docs/contracts 整理）。
- 关键判断：
  - Core2 参数范围以共享常量 `MAX_BLE_RECONNECT_CYCLES = 121` 为准；
  - 未限容两小时 RSS 增长已归因到 TCG translation buffer，但
    `tb-size=128` 的最终两小时结果仍未关闭；
  - public firmware ID/version 不是内容哈希，当前 CDN BIN 必须重新下载、
    计算 SHA 并重新执行；
  - IPv6 namespace cleanup 已改为读取实际 sandbox evidence，完整同 guest
    生命周期仍为 `NOT RUN`。
- 改动范围：README、当前状态、Backlog、工作流、验证台账、代码地图、网络与
  Core2 专题、FirmwareManifest、用户固件矩阵、设备 catalog/profile 生成源，
  以及文档一致性测试。未修改运行中的 QEMU、Device Service、BLE limits 或
  Core2 runner。

## 证据

### 代码或配置

```text
BLE reconnect contract: 1..121 accepted; 122 rejected
Core2 accelerator: tcg,thread=single,tb-size=128
public firmware matrix: resolve current metadata, then force=True download
IPv6 isolation evidence: read sandbox isolation.json cleanup fields
```

### 执行

- 环境：macOS Apple Silicon；Python 平台测试；Node.js client tests。
- 命令：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
node --test platform/tests/test_sha256.mjs platform/tests/test_firmware_upload.mjs
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
ruff check --select E9,F63,F7,F82 platform/tools platform/tests \
  tests/network/ipv6_end_to_end tests/uiflow2/core2_native_hci
```

- 结果：`349/349 PASS`；Node `2/2 PASS`；四类生成物/契约检查和 Ruff
  fatal 检查全部 `PASS`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | `compileall` 和 Ruff fatal 检查通过 |
| transport | `NOT RUN` | 本轮未重跑 QEMU 功能链路 |
| device_response | `NOT RUN` | 本轮是 docs/contracts 对账 |
| data_behavior | `NOT RUN` | 121 轮、IPv6 namespace 和四样本功能重跑待执行 |
| visual_or_physical | `NOT RUN` | 未涉及物理硬件 |

## 当前执行队列

1. 收集正在运行的 Core2 `tb-size=128` artifact-bound `7200s` evidence。
2. 在新 service 上执行 3 个独立 lease × 121 轮 reconnect。
3. 在 privileged Linux namespace 完成 controlled AAAA、allowed IPv6 HTTP、
   denied-port、pcap、cleanup 和 QEMU reap。
4. 重跑当前 AtomS3R/PaperMono 四个刷新样本，并把实际 SHA 写入 evidence。
5. 继续 NET-04 跨主机 executor/reattach 与 companion continuity。

## 验证边界

- 349 项平台测试不等于整机功能矩阵。
- 四个刷新 BIN 的静态分析不等于应用启动、首帧或输入响应。
- Core2 参数允许 121 轮不等于 121 轮已经运行通过。
- IPv6 cleanup 代码和契约 PASS 不等于同一 Linux guest 的完整生命周期 PASS。
- 没有物理硬件、RF、功耗、光学、机械或电气结论。

## 风险与回滚

- 本轮只修改文档、生成源和测试，没有不可逆设备操作。
- 回滚方式：回退源码仓库提交
  `1d3694eea6a4cf39ccfa56e53b8bbb9bfe28b575`。
