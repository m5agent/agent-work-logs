# Core2 tool-hash rebind PR #62 合并 CI 收口

- 日期：`2026-10-30`
- 结果：`PASS`（远端交付）
- 工作类型：`pr_review`
- PR：[#62](https://github.com/m5agent/m5stack-esp-emulator/pull/62)
- Head：`8ebc34109879f6cfd39ba02bbeab74fcd523e84c`
- Merge commit：`674665ea008e65f26aae105ac927e4b1e2909746`
- 主分支 CI：
  [run 40998110196 attempt 2](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40998110196)

## 结论

PR #62 以普通 merge commit 合入 `main`。PR head 与 merge commit 的 Git tree
均为 `42dfdcb9f38ea632462ed6eba59c01843a5abc4c`，没有合并内容差异。

merge commit 的第 1 次 CI 在
`test_unit_host_sensor_evidence` 的 raw report hash 检查失败；PR head CI 和
前一个 `main` commit 均通过。用完全同一 SHA、同一 tree 重跑失败 job 后，
attempt 2 的平台与网络 job 全部通过：

- platform：`1,680` 项，`OK (skipped=10)`；
- network namespace policy：PASS；
- 开放 PR：`0`；
- 没有为这次失败修改源码或放宽测试。

## 边界

这是远端合并与 CI 收口记录，不新增虚拟设备或物理设备结论。原记录中的
Core2 两实例 `4/4` virtual-device 证据、九实例容量拒绝、物理 PSRAM/cache、
controller/RF/电气和真机 `NOT RUN` 边界保持不变。

主工作区仍有 6 个合并前已有的未提交文件，因此本地 `main` worktree 未用
`--ff-only` 覆盖；远端 `main` 已指向 merge commit。
