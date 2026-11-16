# StackChan PR #135 Agent 待办看板与现代码网关评审

- 日期：`2026-11-16`
- 结果：`PARTIAL`
- 工作类型：`pr_review`
- 问题来源：https://github.com/m5stack/StackChan/pull/135
- 源码版本：`yuanxiaoyu/StackChan @ 01b78f686507ae477fede7c62e7cc5f8d92e002b`（base `28b9f0c`）
- 环境：macOS 15（Apple Silicon）、Python 3.12.14 隔离虚拟环境、宿主 CMake/clang、无 ESP-IDF 6.1 工具链

## 结论

PR 的功能思路可行：宿主侧网关与看板 App 的接口契约自洽，作者自带的两组宿主测试可复现通过。
按当前形态仍不建议直接合并：一次 PR 同时引入全局首页手势行为变更、一个不可被现有可见性开关
隐藏的新 App、约 3.0 MB 生成式中文字库，以及一份约 3 万行、来自上游 `kisaragi-mochi/stackchan-mcp`
的网关源码副本。结论覆盖宿主测试与源码级评审；固件构建、虚拟设备与实机画面均为 `NOT RUN`。

## 关键证据

- 固件宿主测试：`ctest` 3/3 通过（model / home gesture / motion）。
- 网关宿主测试：`913 passed, 5 skipped, 1 failed`；唯一失败是 macOS 上 `getaddrinfo` 错误文案
  差异，属环境相关断言，不是产品缺陷；`uv lock --check` 通过。
- 网关运行：实际启动 `serve --transport streamable-http --no-mdns`，未带令牌返回 401，带令牌
  返回 200，JSON 字段与固件解析器逐项一致。
- 源码评审：定位 6 项可核对问题（见 `report.md` 的 F1–F6），全部给出 `file:line`。

## 文件

- `report.md`：完整评审报告与命令
- `run.json`：结构化记录
- `evidence/01-firmware-ctest.log`：固件宿主 CTest 输出
- `evidence/02-gateway-pytest.log`：网关 pytest 输出
- `evidence/03-scope.txt`：diff 规模与 gateway 文件数
- `evidence/04-gateway-dashboard-contract.txt`：看板端点与固件解析器契约核对

## 未覆盖项

- 固件构建 `NOT RUN`：需要 ESP-IDF v6.1 与 `fetch_repos.py` 拉取的 xiaozhi 组件，本机未安装；
  仓库本身也没有固件 CI。
- 虚拟设备 `NOT RUN`：本机 Device Service 有 StackChan（QEMU ILI9342）profile，但 PR 不提供
  可烧录 BIN，自建镜像需先完成上面的工具链步骤。
- 实机 `NOT RUN`：无设备访问；作者文档中的实机结论为自述。
- 因此本记录不给出任何画面、触摸、Wi-Fi 或功耗层面的运行结论。
