# ESP Emulator PR #12 替代合并复评报告

## 背景

- 来源：PR #11 因仓库体积、公开内容脱敏和 CI 可复现性被拒绝合并后，贡献者从当前 main 重建并提交 PR #12。
- 目标：重新核验原三项阻断是否闭环，并检查新分支是否存在新的致命问题；没有问题时执行合并。

## 结论

- 状态：`PASS`。PR #12 满足本次合并前门禁，已合并。
- 根因或关键判断：
  1. 新分支只包含 3 个线性提交，未继承 #11 的大体积历史；独立 clone 无法取得 #11 head 对象。
  2. 新分支从源码中移除了原始 evidence 归档，只保留源码、必要模型资源和有界摘要。
  3. CI 现在安装锁定 Node 依赖，并在无 `.work`、无 `node_modules` 的干净检出通过平台和浏览器门禁。
- 改动范围：Unit 三维外壳和数据模型、UIFlow 同 VM REPL/程序包、Preview/Run、Web 程序面板、QEMU 外设补丁、测试和文档。

## 证据

### 代码与交付范围

PR head 为 `057ce8b5c3f411b05fcf837e383d45cc6dc95bfc`，base 为 `f2061759897955e6017d4aa2a41bd5ba962c35b6`，中间只有 3 个线性提交。

相对 base：

```text
1498 files changed, 206250 insertions(+), 661 deletions(-)
1452 added, 46 modified
new reachable blobs: 1479
new reachable blob bytes: 111757724
new docs/evidence bytes: 0
files greater than 10 MiB: 0
```

PR 自带 `check_pr_scope.py` 同时检查整条分支历史中的新增 blob，可防止“先提交大文件再删除”的绕过方式。独立执行结果：

```json
{
  "status": "PASS",
  "new_blobs": 1479,
  "new_blob_bytes": 111757724,
  "new_evidence_bytes": 0,
  "errors": []
}
```

### 独立 clone 与脱敏

从公开仓库重新 clone main 后，只获取 `refs/pull/12/head` 到本地 review 分支。该 clone 中：

```text
old PR #11 head reachable: NO
working status: clean
repository directory size: 216 MiB
git directory size: 79 MiB
```

新增文本扫描没有发现凭据签名。主机路径和私网地址模式各命中 1–2 个文件，逐一检查后均为测试里的负向样例：字面量通过字符串拼接构造，用于验证敏感内容会被识别，不包含真实主机名或服务地址。

### 执行

环境：

- Python `3.12.14`，安装 Pillow 和 `littlefs-python==0.19.0`。
- Node.js `22.14.0`；`npm ci --prefix platform/tests` 后安装锁定 Playwright Chromium。
- 起点没有 `.work` 或 `node_modules`。

平台测试：

```bash
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
```

结果：

```text
Ran 1237 tests in 63.031s
OK (skipped=3)
```

CI 的 10 组离线 Unit 契约/负控：

```text
Ran 194 tests total
191 passed, 3 skipped, 0 failed
```

Node/Chromium：

```bash
npm run --prefix platform/tests test:contracts
```

8 个入口全部通过，包括实际 Chromium 音频契约和 PreviewClient 门禁。

生成与范围检查：

```bash
python3 platform/tools/check_pr_scope.py \
  --base f2061759897955e6017d4aa2a41bd5ba962c35b6 --head HEAD
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/project_snapshot.py --check
python3 -m compileall -q platform tests
```

全部通过。

fork 中同一 head 的 CI run `40439239199` 状态为 `success`，`platform-contracts` 与 `network-namespace-policy` 两个 job 均通过。因为该 run 是 push 事件，scope step 被跳过；scope 命令已在独立 clone 中单独通过。

### 合并

- PR 状态：`MERGED`
- 合并人：`m5agent`
- 合并时间：`2026-10-27T02:43:51Z`
- merge commit：`8a0d99a03e3205564011bb123e0ee981587bebe7`
- parents：`f2061759897955e6017d4aa2a41bd5ba962c35b6`、`057ce8b5c3f411b05fcf837e383d45cc6dc95bfc`
- `origin/main` 与已验证 PR head 的 tree diff：空

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | 独立 clone 的平台、Node/Chromium、compileall 与生成检查通过 |
| transport | `NOT RUN` | 未启动 QEMU/Device Service 功能会话 |
| device_response | `NOT RUN` | 未执行 Unit/设备数据面回归 |
| data_behavior | `NOT RUN` | 未执行完整 UIFlow2 外设矩阵 |
| visual_or_physical | `NOT RUN` | 未做完整人工视觉验收或物理硬件验证 |
| review | `PASS` | 原体积、脱敏和 CI 阻断均已闭环 |
| delivery | `PASS` | PR #12 已合并，tree 与已验证 head 一致 |

## 验证边界

本次复评覆盖源码交付、静态数据面、离线契约和 Chromium 合成浏览器门禁，没有重新证明真实 Unit/固件数据面。新 `0047` runtime 的 FlashLight 四主机 API/Preview、mounted Web 和完整矩阵仍为 `NOT RUN`。SSE、AIFlow 调用侧、热插拔、保存开机、完整 native/IRQ/thread 清理及物理硬件验证保持开放。

## 风险与回滚

合并后仍保留模型和纹理导致约 112 MB 新增 blob，但低于该 PR 设定的 150 MiB 上限，且没有单文件超限或原始 evidence 归档。如果合并后发现阻断回归，可 revert merge commit `8a0d99a03e3205564011bb123e0ee981587bebe7`；未删除贡献者分支。
