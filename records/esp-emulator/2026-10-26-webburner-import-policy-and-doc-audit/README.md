# ESP Emulator WebBurner import policy and documentation audit

- 日期：`2026-10-26`
- 结果：`PASS`（static import policy and documentation contracts）；firmware
  flash/boot/runtime 与 hardware validation 为 `NOT RUN`
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ 7f9f248](https://github.com/m5agent/m5stack-esp-emulator/commit/7f9f248544fea950fc1b13050f604634ed02637e)
- Base commit：`c00fd2eeed4d180931e9390ed80f3e140359ae74`
- 环境：macOS arm64；Python 3.13；无 firmware flash、QEMU guest 或物理设备

## 结论

WebBurner/M5Burner 包导入现在对路径、资源身份和多 build 选择 fail closed。
ZIP 中危险或不可移植的路径、casefold/NFC 冲突、文件/目录父子歧义和 symlink
会被拒绝；WebBurner manifest、flasher、eFuse、ELF/MAP/SBOM 等资源不能在
多个候选中静默选择排序第一份；多 build 包必须由目标设备 SoC 唯一选择。

同一轮还修正了文档事实边界：自动项目快照把 2026-10-24 的 21 个公开样本
明确标为“历史哈希绑定基线”，不再让页面顶部较新的 evidence 日期暗示它已经
吸收后续刷新、SD fixture、安全与导入结果。当前能力、未完成 Task、运行证据和
历史专题继续分别由状态页、Backlog、验证台账和专题页维护。

## 关键证据

- 平台测试：`543/543 PASS`
- `test_firmware_manifest.py`：`36/36 PASS`
- WebBurner import-policy fixture：`16/16 PASS`
- Manifest policy fixture：`14/14 PASS`
- Secure Boot v2 image fixture：`26/26 PASS`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall 和 `git diff --check`：PASS
- 产品 CI：[40251653367](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40251653367)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 产品提交：`7f9f248544fea950fc1b13050f604634ed02637e`

## 文件

- `report.md`：修复前歧义、实现、验证、边界和回滚；
- `run.json`：机器可读提交、检查项和 evidence；
- `evidence/verification.summary.json`：计数、哈希、CI 和未覆盖边界。

## 未覆盖项

- 没有用公开或厂商真实固件包重跑完整导入、烧录和启动；
- 没有启动 QEMU/esp-emu guest，也没有证明某个镜像可运行；
- 没有验证生产 key、live eFuse、Secure Boot/Flash Encryption 运行态；
- 没有物理 RF、电气、功耗、显示、机械或真机验证；
- 21 个历史公开样本只是基线标签纠偏，本轮没有重新执行它们。
