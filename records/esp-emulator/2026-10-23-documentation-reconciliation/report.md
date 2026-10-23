# 文档与工作流总整理报告

## 背景

近期连续完成了多设备统一运行时、Device Service、网络隔离、FirmwareManifest
和 Core2 native-VHCI 等工作。代码与 evidence 已经前进，但部分入口仍有旧结论：

- `platform/README.md` 仍把网络模拟和 CardputerZero 写成“暂不开放”；
- 统一运行时文档仍说 Core2 VHCI bridge 没有进入 Device Service；
- 网络方案和 QEMU 矩阵对同一路径使用了不同的开放项描述；
- `67/67` 全矩阵发生在 Core2 共享 BB readback 补丁之前，容易被误写成当前
  完整回归；
- 状态、待办、历史排障和单次 evidence 之间缺少统一的阅读顺序。

## 改动

### 当前事实与待办

- 新增 `docs/README.md`，定义当前事实、契约、实现地图、专题和历史证据的
  阅读顺序与更新规则。
- `README.md` 增加文档入口，并把旧全矩阵标记为 `7823bef` 之前的里程碑。
- `docs/project-status.md` 增加工程工作流总表，并明确发布级全矩阵需复跑。
- `docs/project-backlog.md` 增加 `NET-*`、`CORE2-*`、`FW-*`、`SVC-*`、
  `HW-01`、`TAB5-01` 和 `UI-01` 可执行任务板。

### 代码和契约入口

- 重写 `platform/README.md`，反映当前 S3/C6/Core2/Tab5/Linux 运行时分层、
  Device Service 能力、限制和主要工具模块。
- `docs/code-map.md` 接入文档导航，并增加当前结论被推翻时的维护规则。
- `docs/device-service-api.md` 把 Core2 `qemu-wifi`/`qemu-ble` 从
  “experimental”调整为兼容 runtime，指向 canonical
  `qemu-unified` profiles。
- `docs/unified-device-runtime.md`、`docs/network-simulation-plan.md`、
  `docs/qemu-device-adaptation-matrix.md` 和 `tests/uiflow2/README.md`
  统一 `core2-native-vhci` 的已接入与未生产化边界。

### 回归检查

`platform/tests/test_docs_consistency.py` 现在检查：

- 所有 `docs/**/*.md` 都在 `docs/README.md` 有入口；
- Markdown 相对链接、平台 README 和 tests README 链接存在；
- 设备数量与 catalog/profile 动态计数一致；
- 平台测试数量与 `README`、`project-status` 一致；
- Device Service Markdown 和 OpenAPI 版本一致；
- Core2 native-VHCI 已进入服务、当前全矩阵待复跑和已知旧陈述不会回写。

## 验证

```text
platform tests                 215/215 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
OpenAPI 3.1.0 / contract 1.7.0 33 paths PASS
Markdown links                 PASS
documentation index coverage   PASS
git diff --check               PASS
```

源码 main 已推送到 `88c88ab46b23da09c9216bc603133d69bacfb250`。

## 结论边界

本次只整理文档、工作流和文档契约测试，不修改运行时控制器。`67/67` 全矩阵
仍然有效于它记录的旧二进制，但早于 `7823bef` 的 Core2 BB readback 共享
补丁，因此不能作为当前 commit 的 release 级全矩阵结论。发布前需要复跑；
真机验证仍为 `NOT RUN`。

## 回滚

回滚源码提交 `88c88ab46b23da09c9216bc603133d69bacfb250` 可恢复旧文档和
文档一致性测试；不会影响 QEMU、固件、Device Service 状态或物理设备。
