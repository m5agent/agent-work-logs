# ESP Emulator Current Status and Validation Ledger 报告

## 背景

- 来源：用户要求完整整理 ESP Emulator 代码和文档，并结合后来完成的网络、
  Core2 native HCI、WebBurner、FirmwareManifest 和 worker lifecycle 工作
  重新梳理当前任务与待办。
- 现象或需求：多份入口重复保存最新里程碑和阶段状态，历史证据、当前能力和
  Backlog 混在一起，后续更新容易产生漂移。
- 目标：建立稳定的文档职责边界，整理代码域和测试入口，并用契约测试防止
  旧状态和重复完成日志重新写回。

## 结论

- 状态：`PASS`（docs/contracts）。
- 关键判断：把“当前能力”“证据历史”“未完成工作”“复现入口”拆开后，
  页面之间不再各自维护一份最新里程碑表。
- 改动范围：18 个文档/测试文件；没有修改 QEMU、Device Service 运行逻辑、
  固件、外设模型或 API 语义。

## 代码与文档整理

`docs/code-map.md` 现在按五组描述顶层工具：

1. 服务与生命周期；
2. 固件输入与审查；
3. 网络策略与取证；
4. 运行时与设备登记；
5. BLE 与发布工具。

`docs/project-backlog.md` 删除“已经完成/已证明”日志，只保留：

- 任务 ID、状态、下一项最小交付和验收；
- 当前缺口与依赖；
- 不能绕过的前提；
- 发布门禁。

`docs/validation-ledger.md` 保存 2026-10-23 到 2026-10-24 的关键 evidence
入口，并明确它不定义当前能力。

## Core2 状态纠偏

Core2 的页面原先容易把 `HCI-3a` 的 targeted `5/5` 读成完整 native-HCI
里程碑。整理后统一为：

- `HCI-1`：host transport PASS；
- `HCI-2`：首个 stock H2C capture PARTIAL；
- `HCI-3a`：诊断性单包 C2H，`DIAGNOSTIC PASS`；
- `HCI-3b`：完整 HCI/GATT sequence FAIL；
- `HCI-4`：无 GDB repeated lease OPEN；
- GDB 诊断桥、bit-exact controller、物理 cache/PSRAM 和 RF 均未完成。

## 执行

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
node --test platform/tests/test_sha256.mjs platform/tests/test_firmware_upload.mjs
python3 -m compileall -q platform/tools platform/tests tests/network tests/uiflow2
git diff --cached --check
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | Python compileall 与平台测试 |
| documentation contract | PASS | 索引、链接、API 版本、计数、旧状态和 evidence JSON |
| runtime catalog | PASS | runtime coverage、peripheral catalog、QEMU profiles |
| browser upload client | PASS | Node SHA256/upload tests `2/2` |
| GitHub Actions | PASS | run `40038712285`，head `aeb21e2` |
| full peripheral matrix | NOT RUN | 本轮只整理文档和契约 |
| physical hardware | NOT RUN | 未执行真机 |

## 验证边界

文档整理不会产生新的固件、网络、BLE、外设或真机能力。最新功能证据仍以
`validation-ledger` 引用的原始 JSON 和对应源码 commit 为准。

## 风险与回滚

不存在数据删除或设备状态变更。回滚源码提交
`aeb21e2027c3b821098e680fa5cb163d04ed7eec` 会恢复旧文档组织，不改变历史
evidence 或运行资产。
