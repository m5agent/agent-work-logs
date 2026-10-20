# OpenViking: `npx skills add` hangs cloning the full repository

- 日期：`2026-10-20`
- 结果：`PASS`（问题复现、替代方案实测、上游 issue 已提交）
- 工作类型：`issue`
- 上游 issue：https://github.com/volcengine/OpenViking/issues/6328
- 仓库：`volcengine/OpenViking`（public）
- 环境：macOS（Apple Silicon）；`npx skills` 1.5.18；Python 3.13.15；OpenViking 0.4.23（本地服务）

## 结论

官方示例技能的安装命令 `npx skills add https://github.com/volcengine/OpenViking/tree/main/examples/skills/ov-experience-memory`
会检测到 `codex` 并进入非交互安装，但**卡在 `Cloning repository…` 5 分钟以上**。

原因判断：该命令会克隆整个仓库，而仓库约 **374 MB**（GitHub API `size: 383596` KB），目标 skill 只有 **6.9 KB** 的单个 `SKILL.md`。
网络不是问题——同机直连 GitHub 约 3.7 s。

**已验证的替代方案**：

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/volcengine/OpenViking.git
cd OpenViking
git sparse-checkout set examples/skills/ov-experience-memory
```

实测：浅克隆 **25 s**、稀疏检出 **5 s**，`.git` 仅 **1.6 MB**，目标文件完整。

## 关键证据

- 复现：`npx skills` 1.5.18，TTY 下明确显示 `codex Agent detected — installing non-interactively` 后持续 `Cloning repository…`。
- 仓库大小：`size = 383596` KB（约 374 MB）；目标文件 `SKILL.md` = 6891 B。
- 网络对照：`GET https://github.com` → HTTP 200，约 3.7 s。
- 替代方案实测：clone 25 s + sparse-checkout 5 s；`.git` 1.6 MB。
- 内容核对：安装后的 `SKILL.md` 与 `openviking-memory` 插件自带版本逐字节一致。

## 文件

- `report.md`：完整报告（复现步骤、时间线、替代方案、边界）
- `run.json`：机器可读记录
- `evidence/reproduction.txt`：复现与测量明细

## 未覆盖项

- **未验证 `npx skills` 内部实现**：只测了行为，未阅读其源码确认是否使用完整 clone。
- **未测试其他 Agent/平台**：只在 macOS + Codex 下复现。
- **未等待最终完成**：5 分钟后主动取消，未验证"最终能否成功"。
- **上游未回复**：issue 已提交，等待维护者响应。
