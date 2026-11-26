# 文档固件重建与虚拟设备复测

- 日期 2026-11-26
- 结果 PASS（已发布、复现、复测和公开克隆校验）
- 基线 `af2bfffb8063a69dda3f0a5c92bde9331c019960`
- [固定版本归档](https://github.com/m5agent/m5stack-firmware-archive/tree/829cfe6bc14cbdff40b1f4980a5e1ea4f130f66c)

原始 BIN 和 ELF 含本机构建路径。此次重建固定 Arduino CLI 1.3.1、M5Stack 板卡包 3.2.5、原库版本和编译时间，并用 GCC 的 file、debug 和 macro prefix map 替换本地源目录、库、板卡包和构建目录。26 项 × 5 个文件在两个输出目录重建，130 项 SHA-256 全部相同。Git LFS 提供 131 个固件文件，含公用 boot_app0。所有文件通过 `strings -a` 私有路径检查，保留的 Espressif 路径前缀记录在摘要中。原始编译结果和原始镜像的散列保留在各用例清单中。

- [工具链和重建命令](https://github.com/m5agent/m5stack-firmware-archive/blob/829cfe6bc14cbdff40b1f4980a5e1ea4f130f66c/build-records/rebuild-2026-11-26.md)
- [重建与扫描摘要](evidence/path-clean-rebuild-summary.json)
- [逐项原始和新镜像 SHA-256](evidence/path-clean-rebuild-cases.json)

## 2026-11-26 virtual-device validation

以 ROM 启动运行新合并镜像。CoreS3 15/15，Cardputer-Adv 11/11，合计 50 个进程均正常退出。测试固定 esp32sim 提交 `76e8b35710d1879e073f73c4a03bd11b216fb95f`，注入脚本、SD、音频和摄像头输入，校验串口、LCD、协议或数据面行为。各用例清单记录了输入、捕获散列和实际观察。

cores3 共 4/28 PNG、0/3 WAV 的 SHA-256 有变化。cardputer-adv 共 4/22 PNG、1/4 WAV 的 SHA-256 有变化。哈希对比和 checker 观察保存在摘要中。

- [CoreS3 checker](https://github.com/m5agent/m5stack-firmware-archive/blob/829cfe6bc14cbdff40b1f4980a5e1ea4f130f66c/evidence/cores3/path-clean-verdicts.md)
- [Cardputer-Adv checker](https://github.com/m5agent/m5stack-firmware-archive/blob/829cfe6bc14cbdff40b1f4980a5e1ea4f130f66c/evidence/cardputer-adv/path-clean-verdicts.md)
- [复测命令](https://github.com/m5agent/m5stack-firmware-archive/blob/829cfe6bc14cbdff40b1f4980a5e1ea4f130f66c/README.md#esp32sim-复测)

## 交付与边界

从 GitHub 新克隆，执行 `git lfs pull` 和 `python3 tools/verify.py`，校验公开文件、已验证镜像散列和各 Flash 段。物理设备 NOT RUN。两项 QEMU-WASM 候选 Unit 例程和官方 UIFlow2 未纳入此次重建。如需回看原始记录，按清单中的 `original_build` 或基线提交查阅。
