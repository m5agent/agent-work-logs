# OpenViking `npx skills add` 克隆卡顿：复现、替代方案与上游反馈

## 背景

- 来源：按官方说明安装示例技能 `examples/skills/ov-experience-memory`。
- 命令：
  ```bash
  npx skills add https://github.com/volcengine/OpenViking/tree/main/examples/skills/ov-experience-memory
  ```
- 现象：CLI 正确识别 Codex 并进入非交互安装，随后长时间停留在 `Cloning repository…`。

## 结论

- 状态：`PASS`（问题复现、替代方案实测、上游 issue 已提交）
- 根因判断：该安装路径会克隆整个仓库；`volcengine/OpenViking` 约 **374 MB**（API `size` = 383596 KB），
  而目标只是一个 **6.9 KB** 的 `SKILL.md`。同机直连 GitHub 约 3.7 s，排除网络故障。
- 已验证替代方案（约 30 s 完成）：
  ```bash
  git clone --depth 1 --filter=blob:none --sparse https://github.com/volcengine/OpenViking.git
  cd OpenViking
  git sparse-checkout set examples/skills/ov-experience-memory
  ```
  结果 `.git` 仅 1.6 MB。
- 上游反馈：https://github.com/volcengine/OpenViking/issues/6328

## 证据

### 复现

```text
● codex  Agent detected — installing non-interactively
◇ Source: https://github.com/volcengine/OpenViking.git @ main (examples/skills/ov-experience-memory)
◒ Cloning repository…   (5+ minutes)
```

- 两次运行（非 TTY 与 TTY）均未完成；TTY 下可确认已进入 clone 阶段。
- 取消后无任何文件被安装。

### 量化

| 项 | 值 |
| --- | --- |
| 仓库大小（API `size`） | 383596 KB ≈ 374 MB |
| 目标 skill 文件 | `SKILL.md` 6891 B |
| 直连 GitHub | HTTP 200，约 3.7 s |
| 浅克隆 + 稀疏检出 | clone 25 s + sparse 5 s |
| 稀疏 `.git` 体积 | 1.6 MB |

### 内容核对

安装后的 `SKILL.md` 与 `openviking-memory` 插件（0.10.10）自带版本逐字节一致。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `NOT RUN` | 不涉及构建 |
| transport | `PASS` | 官方命令可启动；稀疏克隆与 GitHub Contents API 均成功 |
| device_response | `NOT RUN` | 不涉及设备 |
| data_behavior | `PASS` | 目标文件内容与插件版本一致 |
| visual_or_physical | `NOT RUN` | 不涉及 |
| review | `PASS` | 已量化仓库大小、网络与替代方案耗时 |
| delivery | `PASS` | issue #6328 已提交 |

## 验证边界

1. **未阅读 `npx skills` 源码**：未确认其 clone 参数，仅基于行为判断。
2. **未等其他平台**：只在 macOS + Codex 复现。
3. **未等待最终完成**：5 分钟后主动取消，未验证"最终是否成功"。
4. **上游未回复**：issue 已创建，等待维护者处理。

## 建议（已写入 issue）

- `npx skills` 集成对子目录 URL 使用浅克隆 + 稀疏检出，或走 GitHub Contents API。
- 若无法调整，文档中补充直链下载的备用方式。
- 输出进度/超时，避免静默卡住。
- 可考虑把示例 skills 拆到独立小仓库。

## 风险与回滚

- 不可逆操作：无（仅创建公开 issue 与本地记录）。
- 影响面：无代码变更。
- 数据边界：本记录只含公开仓库、公开 API 数据与公开 issue 链接。
