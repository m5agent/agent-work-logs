# StackChan PR #135 评审报告

## 1. 目标与背景

- 对象：`m5stack/StackChan` PR #135 `feat(stackchan): add agent tasks dashboard and gateway`
- 作者：`yuanxiaoyu`（fork `yuanxiaoyu/StackChan`，分支 `codex/agent-tasks-dashboard`）
- PR 正文为空；已有两条评论（一条外部用户 "nice idea :)"，一条作者中文自动回复）
- 评审目标：判断该 PR 是否可合并，指出可复现的集成问题与验证缺口
- 验收层级：宿主构建/测试 + 源码评审；运行层级（构建、烧录、画面）不在本次覆盖范围

## 2. 变更规模

| 部分 | 规模 |
| --- | --- |
| 全 PR | 149 文件，+113,979 / −52 |
| 固件 App | `firmware/main/apps/app_agent_tasks/` 约 750 行 + 3.0 MB 生成字库（47k 行） |
| 网关 | `gateway/` 109 个受版本控制文件、98 个 Python 文件 |
| 共享固件改动 | `home_indicator.cpp`、`app_setup.cpp`、`main.cpp`、`apps.h`、`tests/` |

## 3. 评审发现

### F1 全局首页手势行为被本次功能 PR 改写（需拆分）

- `firmware/main/apps/common/home_indicator/bottom_swipe.h:34-35`：底边起触区 20 px → 40 px，
  触发距离 50 px → 40 px。
- `bottom_swipe.h:18-22`：阈值在手指仍按下时立即返回 true；原先 `home_indicator.cpp` 只在抬起
  瞬间判定。
- 该手势由所有 App 共享（`home_indicator.cpp` 的 `HomeGesture::update`）。影响面是"在屏幕底部
  40 px 内向上拖动 40 px 即回家"，与列表滚动/底部控件拖动重叠。
- 新测试 `firmware/tests/home_gesture_test.cpp` 只覆盖纯函数状态机，没有覆盖 avatar、launcher、
  app center 等既有页面的回归。
- 建议：单独 PR，附旧行为对照与至少两个既有页面的运行验证；或保持旧阈值与抬起判定。

### F2 新 App 无法被现有可见性开关隐藏

- `firmware/main/main.cpp:45` 直接 `installApp(std::make_unique<AppAgentTasks>())`，没有
  `hal_toggles::register_app_id`。
- `firmware/main/hal/hal_toggles.h:12` 的 `App` 枚举无 AgentTasks 项；`is_app_enabled()` 对未注册
  App 一律返回 true。
- 结果：SETUP → Apps → App visibility 可以隐藏 AI.AGENT / AVATAR / ESPNOW / APP.CENTER / EZDATA /
  DANCE，唯独不能隐藏新增看板；对没有部署网关的普通用户，这是常驻且无功能的菜单项。
- 同一菜单中 `firmware/main/apps/app_setup/app_setup.cpp:149` 使用中文项名 "Agent 看板"，是同屏
  唯一非英文条目；看板与设置页文案也全部硬编码中文，而 App 名与官方 UI 是英文。

### F3 退出 App 时可能阻塞主循环

- `agent_tasks_poller.cpp:157-160`：`stop()` 置位后忙等 `task_running_`；等待对象是正在做 HTTP
  请求的任务。
- `agent_tasks_poller.cpp:16`：单次请求预算 5 s，`client->Open` 为阻塞调用，`stop` 不能中断它。
- `app_agent_tasks.cpp:40`：`onClose()` 调用 `stop()`；Mooncake 的 `onClose` 与 `feedTheDog()` 在同一个
  `main.cpp:47-55` 主循环里。网关不可达（典型场景）时，关闭看板最长可让该循环停 5 s。
- 建议：改为异步收尾（任务自行删除并释放配置），或在退出时主动关闭 socket；并在实机上验证。

### F4 生成字库与包体成本

- `firmware/main/apps/app_agent_tasks/view/agent_tasks_cjk_14.c`：3,047,669 字节、47,278 行、
  7,540 个字形（ASCII + GB2312，14 px / 2 bpp），由 `generate_font.py` 调 `lv_font_conv@1.5.3` 生成。
- 该文件进入 GLOB 编译（`firmware/main/CMakeLists.txt` 的 `apps/*.c`），每个 StackChan 构建都要编译。
- 作者文档记录的镜像为 4,292,768 字节，`ota_0` 分区 `0x4f0000`（5,177,344 字节），余量 17%；
  即余量已经被该字库计入后的结果。建议加 Kconfig/构建开关，或至少减少字库子集。
- 许可处理正确：`view/OFL.txt` + `字体说明.md` 标注 Noto Sans CJK SC / SIL OFL 1.1。

### F5 网关是上游项目的整仓副本

- `gateway/pyproject.toml:2-3,14-15,113-114`：包名 `stackchan-mcp`、版本 `0.20.0`、作者
  `kisaragi-mochi`、Homepage/Repository 指向上游仓库。
- `gateway/LICENSE` 保留上游 MIT 并追加 2026 版权行，`docs/agent-tasks-source.zh-CN.md` 声明来源，
  归属是完整的；问题在交付形态：
  - 约 3 万行中包含 WebSocket 设备控制、拍照 `/capture`、TTS/STT、机器人 handler 等本仓库官方
    固件不使用的路径（作者 README 亦说明需要另一套替代固件）。
  - 无法从 `pyproject.toml` 判断对应上游哪个 commit，后续同步/安全修复成本高。
- 建议：改为依赖上游发行包 + 小补丁；或至少记录上游 commit，并把未使用服务在默认 `serve`
  路径中关闭。

### F6 文档与流程

- `README.md` 顶部插入 59 行中文项目说明，位于官方项目介绍之前，改变了仓库首页定位。
- `docs/superpowers/{specs,plans}/` 属内部规划稿；`docs/design/agent-tasks-official-preview.png`
  已注明是设计示意，不是实机截图。
- 仓库没有固件 CI（仅有 WeCom 转发 workflow），作者文档中的 ESP-IDF 6.1 构建与实机结论无法由
  维护者复现。建议补：构建命令、镜像 SHA-256、一段真机 AGENT TASKS 录屏。

## 4. 执行环境与命令

```bash
# 固件宿主测试
cmake -S firmware/tests -B build-host-tests
cmake --build build-host-tests -j8
ctest --test-dir build-host-tests --output-on-failure

# 网关测试
cd gateway
uv venv --python 3.12 .venv
uv pip install -e . pytest pytest-asyncio ruff
python -m pytest -q
uv lock --check

# 端点契约
STACKCHAN_TOKEN=<throwaway> MCP_HTTP_HOST=<loopback> MCP_HTTP_PORT=<port> \
  python -m stackchan_mcp serve --transport streamable-http --no-mdns
curl /agent-dashboard            # 401
curl -H "Authorization: Bearer ..." /agent-dashboard  # 200
```

## 5. 结果

| 层级 | 状态 | 说明 |
| --- | --- | --- |
| 宿主构建（固件测试） | PASS | 3/3 |
| 宿主测试（网关） | PARTIAL | 913 passed / 5 skipped / 1 failed（环境相关断言） |
| 端点契约 | PASS | 401/200 与字段逐项匹配 |
| 固件构建 | NOT RUN | 缺 ESP-IDF 6.1 与 fetch_repos 组件 |
| 虚拟设备 / 实机 | NOT RUN | 无可烧录 BIN，无设备访问 |

失败用例：`tests/test_cli.py::test_check_port_unresolvable_host_returns_bind_error` 断言
`getaddrinfo failed`，本机 macOS 返回 `Can't assign requested address`；属平台错误文案差异。

## 6. 风险与建议顺序

1. 拆分：首页手势 / 固件 App / 网关 / 文档 四个 PR。
2. 先补 F2（可见性开关）与 F3（退出阻塞），这两项直接影响所有用户。
3. F5 决定网关交付形态后再评估 F4 的包体预算。
4. 提供可复现构建与实机录像，再谈合并。

## 7. 回滚

本次为只读评审：未修改上游仓库、未 push、未关闭 PR；本机仅使用 `/tmp` 下的 fork 克隆与
隔离虚拟环境，可整体删除。
