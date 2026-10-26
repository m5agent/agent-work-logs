# ESP Emulator reading path and metadata drift gate

- 日期：`2026-10-26`
- 结果：`PASS`（documentation/contracts）
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ e6c40e1](https://github.com/m5agent/m5stack-esp-emulator/commit/e6c40e13d4cc3a3aea81ca5f28ff542f7fa44438)
- Base commit：`eb7d80a27166be41f82782e7c104bc82226b6b30`
- 环境：macOS arm64；Python 3.13；无 QEMU guest 启动

## 结论

文档入口现在先回答“当前做到哪、还差什么”，再链接需要深入阅读的代码地图
和专题页；当前事实、待办、生成快照、契约、专题和历史证据有了明确层级。
工程交接、项目状态和 Backlog 新增网络、Core2、FirmwareManifest 三组 P0
的完成项与剩余门禁，已完成的里程碑不再混进待办。

设备 catalog 和 QEMU profile 的验证元数据同步到当前证据：Core2 更新到
`2026-10-26`，AtomS3R/CoreS3/StickS3 吸收后续 WPA2-PSK 正误密码路径，
生成设备档案和项目快照已经重建。

代码侧新增 catalog/profile 漂移门禁：`qemu_profiles.py --check` 会比较
`generated_at`、验证日期和验证状态；负向测试证明手工制造日期漂移时检查会
失败，不再依赖维护者手工同步两份 JSON。

## 关键证据

- platform tests：`531/531 PASS`
- QEMU profile tests：`20/20 PASS`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS
- `compileall` 与 `git diff --check`：PASS
- Ruff `E9/F`：`NOT RUN`，当前 Python 环境未安装 `ruff`
- 产品 CI：[40247778027](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40247778027)
  在 `e6c40e1` 上 `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 产品提交：`e6c40e13d4cc3a3aea81ca5f28ff542f7fa44438`

## 文件

- `report.md`：背景、改动、验证、边界和回滚；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：提交、文件哈希和检查汇总。

## 未覆盖项

- 没有重跑固件或任何 QEMU lease；
- 没有重新生成 firmware/ELF/QEMU-bound 功能 evidence；
- `RUNTIME-03`、`CORE2-02`、`NET-04`、固件运行态安全和真机验证仍未关闭；
- 所有结果只属于 documentation/contract validation，不是硬件或 RF 验证。
