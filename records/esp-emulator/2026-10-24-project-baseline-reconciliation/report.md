# ESP Emulator 当前基线、代码地图与 Backlog 重整报告

## 背景

近期主干连续合入网络 namespace/controlled DNS/TLS、FirmwareManifest
LittleFS、Core2 zero-retry/native-VHCI 和共享 QEMU 修复。当前能力页已多次
更新，但周边文档仍存在三类漂移：

1. Core2 OpenMAC 补丁页仍写 DNS、公网和 BLE `NOT RUN`，而后续同 guest
   和 Device Service evidence 已经通过；
2. 网络方案、统一运行时、外设矩阵和 QEMU 矩阵的日期、最新数字和剩余边界
   不完全同步；
3. Backlog 虽声明“只列未完成工作”，正文却保留大量“已有能力”和“本轮已完成”
   日志，导致完成状态重复维护并快速过期。

目标是建立单一阅读顺序和可执行的新鲜度门禁，让后续代码推进时必须同步入口，
而不是继续在多个页面追加互相矛盾的更新块。

## 改动

### 当前事实与待办

- `README.md` 增加最近里程碑表和明确的重整日期；
- `docs/project-status.md` 增加近期 milestone、evidence 入口和更新后的
  Tab5/Core2/网络边界；
- 重写 `docs/project-backlog.md`，只保留未完成任务、执行顺序和验收条件；
- `docs/README.md` 增加文档新鲜度台账，区分当前事实、契约、专项、历史和
  Backlog，并说明“最近核对”不等于当天重跑所有矩阵。

### 代码与专题文档

- `docs/code-map.md` 增加顶层代码目录、产品入口/非产品入口和 runtime priority；
- 重写 `docs/network-simulation-plan.md`，删除累积运行日志，只保留当前架构、
  已验证、未证明、测试矩阵和下一阶段；
- `docs/firmware-manifest.md` 增加 LittleFS/FAT/SPIFFS 支持矩阵和真实样本统计；
- 统一 QEMU 矩阵、UIFlow2 外设矩阵和 unified runtime 的日期与最新 evidence；
- StopWatch、跨设备回归和多设备设计页加历史边界；
- Core2 OpenMAC/BLE patch、Core2 unified/native-VHCI 和网络 fixture README
  补充后续验证关系。

### 生成元数据

- `devices/catalog.source.json` 与生成的 `devices/catalog.json` 更新为
  `2026-10-24`；
- `platform/qemu/profiles.json` 更新 catalog/validation 日期；
- Core2 blocker 从含糊的 “PSRAM/cache stability remains” 改为
  physical cache/PSRAM timing equivalence `NOT RUN`；
- Core2 validation detail 记录 deterministic icount 10/10、public network 和
  native-VHCI 边界，不再沿用旧 cache/watchdog 根因。

### 文档契约

`platform/tests/test_docs_consistency.py` 新增：

- catalog 与 source 的 `generated_at` 一致性；
- 当前事实页/契约页日期与 catalog 快照一致；
- Core2 blocker 不得回退为旧表述；
- Core2 OpenMAC/BLE patch 页面加入旧状态检查；
- Backlog 必须保留可执行任务板且不得重新出现“本轮已完成”日志。

## 验证

```text
platform tests                 225/225 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
catalog generation             14 devices PASS
Markdown index and links       PASS
obsolete claim checks          PASS
generated_at consistency       PASS
git diff --check               PASS
```

源码 `main` 已推送：

```text
base    eca4120090ad46b12b64ff74b345c38def80804b
result  26090ceb868c66a6b0c338c41f7d242d243f1be2
```

## 验证边界

- 本次只修改文档、生成元数据和文档契约测试；
- 没有重跑 QEMU 67-case 全矩阵；文档继续引用既有
  `67/67`、`274/274` evidence；
- 没有重新执行网络 namespace、TLS、Core2 BLE 或 LittleFS 功能测试；
- 不产生新的 virtual-device 或 hardware validation；
- 物理硬件仍为 `NOT RUN`。

## 风险与回滚

回滚源码提交 `26090ceb868c66a6b0c338c41f7d242d243f1be2` 可恢复旧文档、
旧 profile 描述和旧文档契约测试。该回滚不会改变已构建 runtime、固件、
Device Service 状态或物理设备。
