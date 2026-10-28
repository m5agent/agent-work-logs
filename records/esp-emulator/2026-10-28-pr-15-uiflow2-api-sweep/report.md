# ESP Emulator PR #15 合并审阅报告

## 背景

- 来源：公开 PR #15，`Fix UIFlow2 runtime paths and audit CoreS3/Cardputer APIs`。
- 基线：`47af9e76f89912028db6d9dee0b0bcc5425c852`。
- 原始 head：`3b5c913bc2bf20a05477648bb5d0315b229adaea`。
- 最终 head：`a030d1395636cae5a7064c439295a2153e0a7a89`。
- 合并：`f311c7e0ede2ab98bf05ca8c89c64607575734e3`。

## 改动范围

PR 相对 base 修改 299 个文件，约 `181,539` insertions / `76` deletions。
主要包含：

- CoreS3 SPI2/GDMA、GDMA cursor lifecycle、LCD-CAM DMA/DVP、SPI SD multi-block、
  I2S RX PCM cursor、S3 watchdog 和 Cardputer internal I2C 的 QEMU patches；
- 20 个固定 source preimage/candidate SHA 的 UIFlow2 SDK patches；
- Device Service 的 runtime trace、TTL、audio/storage environment、BLE
  peripheral role、readiness/admission 和 Unit inventory projection；
- CoreS3/Cardputer API inventory、probe runners 和小型 evidence summaries。

原始 firmware、ROM、ZIP、完整日志和凭据没有进入源码分支。

## 审阅结论

聚焦审阅未发现新的致命阻断。PR scope PASS：

```text
new_blobs: 300
new_blob_bytes: 8,379,261
new_evidence_bytes: 610,190
errors: []
```

新增大型 JSON 主要是 API inventory/observation denominators，PR 明确说明它们
不是全 API PASS；失败、BLOCKED_MODEL、UNAVAILABLE_ON_DEVICE 和 pending
cases 仍保留在 evidence 中。

## CI 修复

首轮 CI `platform-contracts`：

```text
Ran 1335 tests
FAILED (errors=2, skipped=3)
```

两个错误均来自新增 C harness 编译，不是 runtime assertion：

- observer cleanup harness 缺少显式 `<stdint.h>`；
- compiler stderr 被 `check=True` 异常吞掉，难以诊断。

Maintainer commit `8091f99d`：

- 两个 harness 显式 include `<stdint.h>`；
- 编译改为断言并输出 stderr。

第二轮 CI 只余：

```text
error: storing the address of local variable 'first' in 'head'
       [-Werror=dangling-pointer=]
```

Maintainer commit `a030d139` 将 fixture 链表节点和 key 改为 static lifetime。
没有 force push、rebase 或改写 contributor commit author。

最终 CI：

- `platform-contracts` PASS；
- `network-namespace-policy` PASS。

## 本地验证

```text
platform tests: 1335 PASS, 3 skipped
runtime coverage: PASS
peripheral catalog: PASS
QEMU profiles: PASS
project snapshot: PASS
PR scope: PASS
diff check: PASS
```

针对两个修复后的 harness：

```text
test_lvgl_custom_animation_patch: PASS
test_lvgl_observer_cleanup_patch: PASS
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| review | `PASS` | 实际 diff、scope、CI 失败和 contributor evidence 审阅 |
| build/contract | `PASS` | Linux CI、1335 platform tests、四个 generated checks |
| runtime | `REVIEW` | PR 附带 28-patch runtime、matrix 和 service evidence；本次未独立重跑 |
| data_behavior | `REVIEW` | PR 附带 camera/SD/PCM/Canvas/Web/network/SDK A/B evidence |
| visual_or_physical | `NOT RUN` | 本次没有本地视觉或硬件执行 |
| delivery | `PASS` | PR 两 jobs 全绿后 merge |

## 验证边界

- 本次是聚焦合并审阅，没有逐 method 重跑 API sweep。
- PR 中的 `68/68` matrix 和所有专用 sessions 不由本次记录重新认证。
- 物理硬件、RF、功耗、电气、机械、光学均为 `NOT RUN`。
- UIFlow1/LVGL7 和 pending stock/high-level cases 仍按 PR 文档保持开放。

## 风险与回滚

没有启动本地 Device Service 或 QEMU，未产生本地 session。源码回滚可 revert
merge `f311c7e0ede2ab98bf05ca8c89c64607575734e3`。Contributor history 保留，
新增维护提交只包含 test portability 修复。
