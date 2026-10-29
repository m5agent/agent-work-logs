# ESP Emulator SVC-03 stateless parsing boundary 报告

## 背景

- 来源：`SVC-03`，PR
  [#43](https://github.com/m5agent/m5stack-esp-emulator/pull/43)。
- 问题：`device_service.py` 同时承担错误、解析、存储、runtime、evidence 和
  lifecycle orchestration，维护边界过大。
- 目标：只移动一个无状态、可回滚边界，不改变 API、错误码或证据结构。

## 结论

本次迁移 `ServiceError` 与四个小型 parser/validator。原模块继续以同名对象
re-export，调用点无需更改。新增测试直接验证 public symbol identity、错误
payload 和边界行为。

## 改动范围

- 新增 `device_service_errors.py`：`ServiceError`。
- 新增 `device_service_parsing.py`：`parse_int`、`parse_size`、
  `parse_capture_pcap`、`is_sha256`/`_is_sha256`。
- `device_service.py` 删除重复实现并从新模块导入。
- 新增 `test_device_service_parsing.py`。
- 更新 Backlog/status/workstream/code-map/validation ledger/snapshot。

没有修改 `/api/v1` 路由、HTTP status、错误 code、session JSON、evidence
ZIP、历史恢复、运行参数、QEMU 路径或状态机。

## 执行

```bash
python3 platform/tests/test_device_service_parsing.py
python3 platform/tests/test_device_service.py
python3 -m unittest discover -s platform/tests -p 'test_*.py'
ruff check \
  platform/tools/device_service_errors.py \
  platform/tools/device_service_parsing.py \
  platform/tests/test_device_service_parsing.py
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | Python imports and full platform suite |
| transport | NOT RUN | no transport path changed |
| device_response | NOT RUN | no runtime/device path changed |
| data_behavior | PASS | parser/error contract tests |
| visual_or_physical | NOT RUN | not applicable |

平台回归 `1569 OK, 10 skipped`；service contracts `124/124 PASS`；新边界
`7/7 PASS`。CI 的两个 platform-contracts 和两个 network-namespace-policy
job 均通过。

## 验证边界

这是代码边界迁移，不是运行态 ACL、guest filesystem ACL 或服务池完成。
`SVC-03` 的后续拆分仍需逐步重跑受影响 tool-hash-bound evidence。

## 风险与回滚

风险限于导入错位、错误 payload 或 parser 行为漂移，已由 symbol identity 和
行为测试覆盖。回滚 merge commit 可恢复单体实现，不涉及数据迁移。
