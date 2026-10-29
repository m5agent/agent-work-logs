# ESP Emulator operator runtime ACL

- 日期：`2026-10-29`
- 结果：`PASS`（host-runtime validation）
- 工作类型：`code_change`
- 问题来源：[PR #28](https://github.com/m5agent/m5stack-esp-emulator/pull/28) / `FW-01`
- Base：`39544effb0e266d0463da33d80f347a708c07423`
- 实现提交：`7bf978e9265e44d43595aeb29ea9a15bf9128247`
- 合并提交：`ad4bce62a6750aa67eb8269c401b5aebc5b16982`
- 环境：macOS arm64；真实 Device Service HTTP；无 QEMU guest

## 结论

Device Service API/OpenAPI 升至 `1.51.0`，新增 operator-owned runtime ACL。
策略只能来自外部 regular JSON 文件，不能由固件 metadata 自授权。配置后按
设备限制 serial/input/reset、program execute/interrupt/read、guest package
write 和 flash read；未声明设备或操作默认 deny。Session 与 capacity 响应暴露
semantic policy SHA256 和有效权限，denied program/serial/log/flash 数据会从
snapshot/evidence 脱敏。

真实 HTTP runner 通过 `23/23` checks，包括 allowed/denied operation、
package 路径 ACL、denied event、数据脱敏、无效策略启动失败、有效 `SIGHUP`
reload 与后续无效 reload 保留旧策略。全平台实现回归为
`1550 OK + 10 skipped`。

## 关键证据

- OpenAPI SHA256：
  `a9bdbe8a8339a847b7e08244d39304423e005ed902c1979443d72340cbc3e921`
- machine evidence SHA256：
  `05e3be3ceab4ba2382293d08a93443815fceee2d6c7bd11c99c84dcf6b25bbda`
- policy example SHA256：
  `cca8710adf1a3e9914da389bcfb9e6346dcb9a4b51002417db6f7174411aa044`
- runtime ACL tool SHA256：
  `2dd9c7b84e5d82baafc3d3b8495df1e8d667d7765c6eb8c9aa7d740a76dc06e0`
- Device Service SHA256：
  `16d668162b8100876ce3c681ad0a3a35b695c4a6ce1d910f13ec990a6750750c`
- [PR #28](https://github.com/m5agent/m5stack-esp-emulator/pull/28) 的 push/PR
  CI `40841685928`、`40841710209` 与合并后 main CI `40842083370` 均 PASS。

源码证据：

- [runtime ACL evidence](https://github.com/m5agent/m5stack-esp-emulator/blob/ad4bce62a6750aa67eb8269c401b5aebc5b16982/docs/evidence/2026-10-29-runtime-acl/README.md)
- [machine evidence](https://github.com/m5agent/m5stack-esp-emulator/blob/ad4bce62a6750aa67eb8269c401b5aebc5b16982/tests/firmware/evidence-2026-10-29-runtime-acl.json)
- [runner](https://github.com/m5agent/m5stack-esp-emulator/blob/ad4bce62a6750aa67eb8269c401b5aebc5b16982/tests/firmware/runtime_acl/run_test.py)

## 文件

- `report.md`：实现、策略语义、执行、边界与回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary

## 未覆盖项

- firmware/guest filesystem 自身 ACL 与文件权限强制执行；
- arbitrary native firmware sandbox、guest/controller quiescence；
- QEMU guest 与 virtual-device 功能路径；
- physical hardware、RF 或电气验证；
- 完整许可覆盖与法律审批。
