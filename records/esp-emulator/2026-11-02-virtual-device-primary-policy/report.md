# 虚拟设备优先验证政策收敛报告

## 背景

用户指出当前项目仍出现 Tab5 真机前置要求，并明确说明以后虚拟设备是主力，
真机只会在少数场景使用。要求定位这是项目说明还是全局说明，并删除对应要求。

## 定位结果

### 全局说明

`~/.codex/AGENTS.md` 没有 Tab5 专属真机要求。其 External Verification Gate
已经允许：

```text
Physical hardware and validated virtual devices are both accepted evidence sources.
```

同文件还明确，QEMU、esp-emu 或项目批准的 virtual device 在覆盖同一实现路径时
足以支持 external publication，只要求准确标注 validation class。

因此本次没有修改全局 AGENTS。

### 项目说明

Tab5 专属硬门槛位于 `docs/tab5-deferred-backlog.md`：

```text
real-hardware validation is completed before any external claim that the
fix is production-ready.
```

项目还把通用的 `HW-01 真机同路径`列为 P0，并同步散落在：

- `docs/project-backlog.md`；
- `docs/project-status.md`；
- `docs/workstreams.md`；
- `docs/engineering-handoff.md`；
- `docs/project-snapshot.md`（生成文件）。

## 改动

1. 删除 Tab5 deferred backlog 的 real-hardware production-ready 前置条件。
2. 将 Tab5 描述改为“当前已建模工作流的 primary virtual host”，同时保留 full
   peripheral data plane 仍 deferred 的事实。
3. 删除 `HW-01` P0、Task、依赖、workstream 和状态索引。
4. 删除 Unit 验收里的“真机同路径另验”和 CardputerZero 默认真机边界要求。
5. 保留物理声明边界：
   - 默认功能验证使用 validated virtual device；
   - 只有明确声称 RF、功耗、声学、光学、机械或电气属性时才附加物理验证；
   - virtual-device PASS 不能写成 hardware PASS。
6. 更新 Current Status、Backlog、Workstreams、Engineering Handoff、Validation
   Ledger 和生成 Project Snapshot。
7. 增加文档契约：
   - `HW-01` 不得回流；
   - Tab5 不得重新出现 real-hardware production prerequisite；
   - Tab5 必须声明 primary virtual host。

## 验证

文档/契约命令：

```text
PYTHONPATH=platform/tools:. python3 -m unittest discover \
  -s platform/tests -p 'test_docs*.py'

Ran 50 tests
OK

python3 platform/tools/project_snapshot.py --check
PROJECT_SNAPSHOT_OK

git diff --check
PASS
```

PR #79 head 的四个 CI checks 全部成功。
PR #79 普通 merge 为 `8dd390ff810032b3cbdf7c2d18fda4e97dade8bd`；
合并后 main CI `41396758444` 的 `platform-contracts` 与
`network-namespace-policy` 均成功。

## 影响

- 默认工程和审查工作流不再等待物理设备。
- 同一 firmware/runtime/profile 的 validated virtual-device evidence 可直接支持
  功能发布结论。
- Tab5 仍为 `partial`；本次改变的是验证路径优先级，不是外设模型完成度。
- 物理属性专用验证仍按需独立记录。

## 未覆盖

本轮没有执行 QEMU、固件、浏览器虚拟设备或物理硬件。验证范围仅为文档一致性、
生成快照和契约测试。

## 回滚

回退 PR #79 即可恢复旧文档和 `HW-01` 任务。若回滚，只影响验证政策与文档契约，
不会修改任何运行时模型或固件。
