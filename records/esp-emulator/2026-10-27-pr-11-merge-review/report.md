# ESP Emulator PR #11 合并前审查报告

## 背景

- 来源：公开仓库 PR #11，目标是整合 Unit 模拟、同 VM UIFlow 实时程序、Preview/异步 Run、Unit 控制器模型及相关证据。
- 现象或需求：用户要求做一次合并前审核；如果没有致命问题就合并。
- 目标：确认 PR 是否满足仓库的合并、公开交付和最低回归门禁，而不是宣称新增功能已在真机或完整矩阵中通过。

## 结论

- 状态：`FAIL`。当前不满足合并条件，未执行合并。
- 根因或关键判断：
  1. PR 把大量本应位于工作记录/对象存储的原始证据直接加入公开源码仓库，导致一次新增 `84,586` 个文件、约 `2.27 GB` 工作树内容。
  2. 新增公开内容未通过仓库脱敏规则：`511` 个文件包含主机绝对路径，`203` 个文件包含私网 IPv4 地址。
  3. PR 声称的 CI 门禁在干净检出中不可复现：平台套件有 `19 failures + 1 error + 3 skipped`；新增 Node 测试依赖 `playwright`，但 workflow 没有安装该依赖。
- 改动范围：核心 Python 服务、UIFlow REPL/程序包生命周期、Preview 服务、Web 前端、Unit catalog、QEMU patches、应用测试和大量 evidence 快照。

## 证据

### 代码或配置

PR head 为 `a37342f61c05964c060719a6e35c2d568c828e84`，base 为 `f2061759897955e6017d4aa2a41bd5ba962c35b6`。GitHub 报告 PR `MERGEABLE`，但 merge state 为 `UNSTABLE`，且没有任何 check rollup。

相对 base 的差异摘要：

```text
84586 files changed, 26008003 insertions(+), 656 deletions(-)
84540 added, 46 modified
```

分支树的常规文件内容约 `2,271,719,924` bytes，base 约 `27,065,574` bytes。`docs/evidence/` 占 `83,096` 个新增文件；扩展名分布包含 `380` 个 ZIP、`4,280` 张 PNG、`22,734` 个 `.raw` 和 `13,445` 个 JSON 文件。

脱敏扫描只输出命中文件数，不复制敏感值：

```text
added files with host-local absolute paths: 511
added files with private IPv4 address strings: 203
confirmed credential-signature matches: 0
```

抽查 `.github/workflows/ci.yml` 发现新增的 Node 测试包含 `test_unit_annotation_bridge.mjs` 和 `test_unit_audio.mjs`，但 workflow 没有执行 `npm ci` 或其他 Node dependency install。PR 中虽然存在 `platform/tests/package-lock.json`，CI 未使用它。

### 执行

- 环境：macOS，Python 3.13.15 临时 venv，安装 Pillow 与 `littlefs-python==0.19.0`；Node.js 22.14.0。
- PR 工作树：从 `refs/pull/11/head` 创建 detached worktree，不修改用户主工作树。

生成器与编译检查：

```bash
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/runtime_coverage.py --check
python3 -m compileall -q platform tests
```

结果为全部通过。

平台测试：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
```

结果：

```text
Ran 1226 tests in 78.708s
FAILED (failures=19, errors=1, skipped=3)
```

失败分类：

- `18` 个 Unit host evidence 测试依赖未随干净检出提供的 `.work` 基线文件。
- `1` 个文档链接测试发现缺失的 `promoted-warning-strict.log`。
- `1` 个 Unit host sensor evidence 测试在创建临时 `.work` 目录时因目录不存在报错。

浏览器/Node 门禁：

```bash
node platform/tests/test_sha256.mjs
node platform/tests/test_firmware_upload.mjs
node platform/tests/test_unit_visual_mappings.mjs
node platform/tests/test_frontend_recovery.mjs
node platform/tests/test_unit_annotation_contract.mjs
node platform/tests/test_unit_annotation_bridge.mjs
node platform/tests/test_unit_audio.mjs
```

前五项完成；`test_unit_annotation_bridge.mjs` 在干净检出中因 `ERR_MODULE_NOT_FOUND: playwright` 中止，后续 audio 测试未执行。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall、QEMU profile、catalog、runtime coverage 通过 |
| transport | `NOT RUN` | 未启动 QEMU 或 Device Service 功能会话 |
| device_response | `NOT RUN` | 未执行 Unit/设备数据面回归 |
| data_behavior | `NOT RUN` | 未执行完整 UIFlow2 外设矩阵 |
| visual_or_physical | `NOT RUN` | 未做真实浏览器视觉验收或物理硬件验证 |
| review | `FAIL` | 合并门禁存在仓库体积、脱敏和 CI 阻断项 |
| delivery | `FAIL` | 不满足“无明显致命问题时合并”的条件 |

## 验证边界

本次是合并前风险审查，不是新增功能的完整验收。没有逐文件审阅 `docs/evidence/` 的全部 83,096 个文件，也没有执行 20–30 分钟完整 UIFlow2 矩阵。代码功能的局部正确性不能抵消公开内容、仓库体积和 CI 的阻断问题。

建议的解除条件：

1. 从源码 PR 中删除原始 evidence 树、浏览器 trace、截图、ZIP 与生成文件；只保留小型总结、哈希、可重建命令，并把完整证据归档到工作记录仓库或 artifact storage。
2. 对保留的文档与测试 fixture 做严格脱敏，清除主机绝对路径、私网地址和任何设备/会话唯一标识。
3. 修正 CI：在 Node 测试前按 lockfile 安装依赖；在干净检出中创建测试所需的临时目录或移除对本地 `.work` 的隐式依赖；补齐缺失的相对链接。
4. 重新在全新 clone/worktree 中运行与 PR 声明一致的门禁，并取得 GitHub check；再按风险执行受影响设备组或完整矩阵。
5. 完成上述步骤后重新评估 PR。由于当前分支已包含约 2.27 GB 历史对象，若 PR 被直接 amend/force-push，需要确认贡献者接受改写；若不改写，则需要关闭旧 PR，用清理后的新分支重建。

## 风险与回滚

未执行任何 GitHub merge、注释、分支修改或硬件操作。临时 worktree 和 Python venv 只用于审查，可从 `/tmp` 清理；PR 与远端分支保持不变。主要风险是若直接合并，仓库历史将永久保留这批大体积对象，即使后续删除工作树文件也无法从历史中消除。
