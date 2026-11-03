# QEMU 构建产物的公开路径修复

- 日期：`2026-11-03`
- 结果：**PASS（限定子结果）**：producer 修复、全 fresh 构建、实际产物路径审计及 Cardputer-ADV 同路径虚拟设备验证通过。完整 20 例仍在运行，preview 尚未发布。
- 工作类型：`code_change`、`report`
- 问题来源：发布前发现构建机私有路径进入旧本地 QEMU WASM，需要从 producer 修复并重新构建，不能重写成品掩盖问题。
- 源码版本：[1b86ed6f7edcc36deafc4834b45a28c6a6017c79](https://github.com/m5agent/m5stack-esp-emulator/commit/1b86ed6f7edcc36deafc4834b45a28c6a6017c79)，base 为 [189dc01a5ee42a23ac7e246f8390c2acfe471ffa](https://github.com/m5agent/m5stack-esp-emulator/commit/189dc01a5ee42a23ac7e246f8390c2acfe471ffa)。
- 环境：固定 Emscripten `3.1.50`，单一 QEMU/TCI WASM；Cardputer-ADV 使用 Chrome `156.0.8078.80` 与 Apple M4 Metal 模型画布。无物理设备测量。

## 结论

修复在 C/C++ 编译时映射源路径，并把 GLib 配置为公开逻辑安装路径，再经 staged 安装仅重定位 host 查找所需 `.pc` prefix。没有修改 QEMU C 补丁、source lock、时钟或断言策略，没有对 WASM 进行后处理。8 个库和 QEMU 均 fresh 构建；实际新 WASM 为 `3c6b249002d83118e0ddcbd82e4ee6336223293b98566fc7709d5087d9df4567`，`12745460` bytes，14 个 section 的实际 producer 路径命中为零。

新 runtime 的 Cardputer-ADV reference case **69/69 PASS**：同一实际固件完成串口 ready、11 键原驱动 FIFO 输入、帧与模型 texture 一致性、pause/resume 和退出；6 个真实 CDP Worker target 全部关闭。此结果不代表完整 20 例通过、所有设备提速或 Pages 已更新。

## 关键证据

- [fresh-build-summary.json](evidence/fresh-build-summary.json)：新 build/runtime/source 身份、1446 步 QEMU 构建与旧产物撤回计数。
- [runtime-independent-summary.json](evidence/runtime-independent-summary.json)：6 runtime 文件、14 WASM section、源码包和 8 个 fresh 库的独立审计。
- [prepared-export-summary.json](evidence/prepared-export-summary.json)、[allasset-prefix-summary.json](evidence/allasset-prefix-summary.json)：2127 个导出资源身份和已分类路径检查；不是发布回执。
- [cardputer-adv-validation-summary.json](evidence/cardputer-adv-validation-summary.json)：原始报告 `7f9f5f7fc53eebcf4a1fea63f38f673f67cbdbc6a652ede6c2c579951e30192f` 的白名单派生，真实串口/输入/帧/目标关闭证据；session/target IDs 只保留 SHA-256。
- [producer-host-summary.json](evidence/producer-host-summary.json)：17 bootstrap、10 exporter host 合同及保留的失败前置历史。

## 文件

- [report.md](report.md)：根因、变更、验收范围、复现与回滚。
- [run.json](run.json)：机器可读的限定结果。
- `evidence/`：审核后的 summary；不包含原始 endpoint、构建机路径、ROM/固件/Flash。
- [repair.patch](patches/0001-qemu-public-producer-paths.patch)：base→target 的完整 4 文件补丁；[应用验证](evidence/repair-patch-summary.json)通过。
- `code/`：不适用；代码在固定源码提交，未重复复制工程。

## 未覆盖项

完整 20 例、线上部署和线上实际 guest 不在本子记录的 PASS 范围。正式 CI `41617152984` 的 e950 engine target 关闭失败和 skipped deployment 独立保留，Cardputer-ADV 通过不关闭该问题。Factory 固件缺口、任意固件、长时间稳定性、物理/RF/功耗行为仍未解决或未运行。
