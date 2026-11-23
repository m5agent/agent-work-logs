# m5stack 公开仓库记录

| 日期 | 主题 | 结果 | 记录 |
| --- | --- | --- | --- |
| 2026-11-23 | M5Cardputer-UserDemo #48 工具链政策与 ESP-IDF 6.1 构建实测 | PASS（v6.1 真实构建：usb 组件移除 + M5GFX C23 bool 两处失败；5.4.2 构建 NOT RUN） | [查看](2026-11-23-cardputer-userdemo-issue-48-latest-toolchain/) |
| 2026-11-23 | M5Cardputer-UserDemo #48 rich-click/bitarray 构建报错归因 | PASS（host-level 复现检查脚本行为；4.4.6/6.1 构建 NOT RUN） | [查看](2026-11-23-cardputer-userdemo-issue-48-idf-python-env/) |
| 2026-11-23 | esphome-yaml #127 ESPHome 2026.11 addressable light 兼容性 | PARTIAL（2026.11/2026.10 构建 PASS；虚拟设备像素读回 PASS；实机与 LED 输出 NOT RUN） | [查看](2026-11-23-esphome-yaml-pr-127-addressable-light/) |
| 2026-11-23 | AIFlow #6「Run Always」下载路径重复的虚拟设备复现 | PARTIAL（虚拟设备复现；云端上传与实机 NOT RUN） | [查看](2026-11-23-aiflow-issue-6-run-always-path/) |
| 2026-09-18 | 公开仓库零评论 Issue 盘点与可回复性评估 | REVIEW（盘点）+ PARTIAL（5 条 issue 的 host/编译级闭合验证） | [查看](2026-09-18-recent-unanswered-issues/) |

## 说明

本目录记录对 `github.com/m5stack` 公开仓库 Issue 的盘点、核对与验证，供在 Issue 中引用。

记录只包含公开仓库、公开 commit SHA 和公开 API 数据。
