# ESP Emulator current-work and documentation consolidation

- 日期：`2026-10-26`
- 结果：`PASS`（documentation/contracts）；firmware/QEMU functional rerun 与
  hardware validation 为 `NOT RUN`
- 工作类型：`report`
- 源码版本：
  `https://github.com/m5agent/m5stack-esp-emulator/commit/ad1d878d73af0d8b99e2a47809414f671c432bf3`
- Base commit：`eff1561e9f0da700c843ed14d9019c81f1e27e55`
- 环境：macOS arm64；Python 3.13；本地 Node `v22.14.0`；QEMU guest
  `NOT RUN`

## 结论

ESP Emulator 的总览、当前状态、Backlog、工作流和 QEMU 适配页已经重新分层。
当前页面只维护能力、边界、调查假设和下一步；运行轮次、PASS 比例、RSS 和
工具哈希统一留在验证台账与 evidence。`RUNTIME-03` 现在明确记录
flash-cache/IPC/DPORT 交接只是尚未证实的调查假设，S32C1I 锁空闲只否定了
首要锁泄漏解释。被 `core2-native-hci` 取代的 GDB/VHCI 页面也统一标成
historical/diagnostic，避免把旧 `current 1/2` 当成本周产品状态。

本次没有改变 Device Service、QEMU 或固件行为。代码审计确认主要债务仍是
`device_service.py` 的编排边界，但 Core2 并发 evidence 绑定了该文件的 tool
hash，因此任何拆分都必须配套重跑受影响 evidence，不能直接让新代码继承旧
PASS。

## 关键证据

- 文档契约：`39/39 PASS`；
- 全平台测试：`499/499 PASS`；
- Node SHA256、WebBurner upload 与 UI smoke：PASS；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall、selected Ruff `E9/F` 与 `git diff --check`：PASS；
- 产品 CI：[CI 40210161366](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40210161366)
  在 `ad1d878` 上两个 job 全部成功。

## 文件

- `report.md`：背景、改动、代码边界、验证和回滚；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：验证项、提交和剩余边界。

## 未覆盖项

- 没有重跑 UIFlow2 全量、Core2 并发/长稳或其他 QEMU 功能矩阵；
- 没有重新生成任何 firmware/ELF/QEMU-bound runtime PASS；
- 没有真机、RF、功耗、声学、光学、机械或电气验证；
- `RUNTIME-03` 的 flash-cache/IPC/DPORT 假设尚未得到匹配源码/ELF 证实。
