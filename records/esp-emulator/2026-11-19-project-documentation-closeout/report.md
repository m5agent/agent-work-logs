# 项目文档整理与发布回读

仓库入口、文档导航和待办累积了历史交付细节。将当前入口、未完成验收条件和历史文档索引放回各自的项目维护文件。旧的证据正文仍可从登记册访问。

| 文件 | 原行数 | 新行数 |
| --- | ---: | ---: |
| [README.md](https://github.com/m5agent/m5stack-esp-emulator/blob/cc25a8a8ac083e00608d591281289f1452cc75ac/README.md) | 125 | 61 |
| [README.en.md](https://github.com/m5agent/m5stack-esp-emulator/blob/cc25a8a8ac083e00608d591281289f1452cc75ac/README.en.md) | 130 | 61 |
| [docs/README.md](https://github.com/m5agent/m5stack-esp-emulator/blob/cc25a8a8ac083e00608d591281289f1452cc75ac/docs/README.md) | 879 | 51 |
| [docs/document-register.md](https://github.com/m5agent/m5stack-esp-emulator/blob/cc25a8a8ac083e00608d591281289f1452cc75ac/docs/document-register.md) | 0 | 312 |
| [docs/project-backlog.md](https://github.com/m5agent/m5stack-esp-emulator/blob/cc25a8a8ac083e00608d591281289f1452cc75ac/docs/project-backlog.md) | 1007 | 306 |

两次提交分别重整文档、修复 Unit 历史证据校验的定位。第一轮平台回归暴露了仍指向旧导航的校验，第二轮完整回归通过，共运行 2,516 项，跳过 10 项。覆盖率、外设、运行配置、项目快照和提交范围检查通过。

```sh
PYTHONPATH=platform/tools python3 -m unittest discover -s platform/tests -p 'test_*.py'
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
python3 platform/tools/project_snapshot.py --check
git diff --check
```

GitHub main 回读与整理后的提交一致。中英文首页、导航、登记册和待办的远端 Git blob 字节标识与本地提交一致。GitHub 实际渲染的中文首页包含当前状态、剩余工作和展示图。改动可通过对应提交的 Git 差异复核及回退。

本轮范围包括文档和相关校验。实机、虚拟设备固件验证和独立 GitHub Pages 部署均为 NOT RUN。待办继续由项目 Backlog 保存。
