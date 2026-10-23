# agent-work-logs

`m5agent` 的工作记录仓库，分两层发布。

| 层 | 目录 | 发布目标 | 内容 |
| --- | --- | --- | --- |
| 对外 | `records/` | 内部 GitLab + 公开 GitHub | 公开仓库的 Issue 处理、PR/MR 评审、公开库的硬件或构建验证、可复现缺陷分析 |
| 内部 | `internal/` | **仅内部 GitLab** | 内网运维、环境配置、权限盘点、服务部署、内网服务排查 |

两层内容互不混合。公开层会原样出现在公开仓库，因此公开层里不允许出现任何内网信息。

## 发布

```bash
./scripts/publish.sh
```

脚本做两件事：

1. 把完整仓库（含 `internal/`）推送到内部 GitLab。
2. 把公开子集（`records/`、`docs/`、`templates/`、根文件）重建为单个提交，强制推送到公开 GitHub。

公开仓库由公开子集同步而来，保留**线性追加历史**（不重写），因此对外记录可以安全地用固定 commit permalink 引用。

## 判断该放哪一层

只要回答一个问题：**这条记录对外部读者有价值吗？**

- 有价值 → `records/`
- 只是本机或内网的操作记录 → `internal/`
- 拿不准 → 放 `internal/`。宁可少公开，也不要把内网细节推出去。

配置企业微信、安装本机工具、调整访问控制、盘点内网权限这类操作，都属于 `internal/`。

## 记录格式

- [工作流](docs/work-record-workflow.md)
- [记录格式](docs/record-format.md)
- [脱敏规则](docs/redaction-policy.md)
- 模板：[templates/work-record/](templates/work-record/)

## 结果等级

`PASS` / `PARTIAL` / `FAIL` / `NOT RUN` / `REVIEW`。一条记录可以同时包含多个层级结果，
不要用单一总状态掩盖未覆盖项。

## 对外记录索引

| 2026-09-18 | m5stack 公开仓库 | 公开仓库零评论 Issue 盘点与可回复性评估 | REVIEW（盘点）+ PARTIAL（5 条 host/编译级闭合验证） | [查看](records/m5stack-github/2026-09-18-recent-unanswered-issues/) |
| 2026-09-21 | ESP32-P4 Flasher | 可配置 DUT 烧录波特率，默认 1.5 Mbaud | PARTIAL（构建/中心测试通过；实机烧录未执行） | [查看](records/esp-flasher-by-esp32p4/2026-09-21-configurable-flash-baud/) |
| 2026-10-10 | UIFlow MicroPython | StamPLC `boot_option=2` Wi-Fi 启动跳过 PoE 初始化 | PARTIAL（host 复现 + 构建 PASS；无 StamPLC 实机） | [查看](records/m5stack-github/2026-10-10-uiflow-issue-116-stamplc-wifi/) |
| 2026-10-10 | UIFlow MicroPython | RTC 同步改用 UTC，修复重启时钟漂移 | PASS（StopWatch 实机 + 构建；StamPLC 未单独复测） | [查看](records/m5stack-github/2026-10-10-uiflow-issue-117-rtc-utc/) |
| 2026-10-10 | m5stack-linux-dtoverlays | aw882xx 支持 Linux 6.13+ 头文件 | PARTIAL（6.12/6.14 构建 PASS；未做 insmod/音频） | [查看](records/m5stack-github/2026-10-10-dtoverlays-issue-14-aw882xx-kernel/) |
| 2026-10-23 | ESP Emulator | StickS3 公网 HTTP 闭环与第三方固件 NTP 超时定位 | PASS（virtual-device validation；NTP 应用层失败单列） | [查看](records/esp-emulator/2026-10-23-sticks3-public-network-closure/) |
| 2026-10-23 | ESP Emulator | StickS3 社区天气固件网络、显示与按键验证 | PARTIAL（virtual-device follow-up：QIO/NVS/LittleFS/实时天气/完整八页/语音已闭环；双击固件缺陷与实体硬件未通过） | [查看](records/esp-emulator/2026-10-23-sticks3-community-weather-functional/) |
| 2026-10-23 | ESP Emulator | `.work/` 运行资产缺失的部署诊断与结构化错误 | PASS（fresh clone + virtual-device session；物理硬件未测） | [查看](records/esp-emulator/2026-10-23-runtime-assets-deployment/) |

## 目录结构

```text
agent-work-logs/
|-- records/<target>/<YYYY-MM-DD>-<topic>/       # 对外
|-- internal/records/<target>/<YYYY-MM-DD>-<topic>/  # 仅内网
|   |-- README.md  report.md  run.json
|   `-- evidence/  patches/  code/
|-- docs/
|-- templates/
`-- scripts/publish.sh
```

## 安全约束

- 公开层不得出现 token、密钥、内网 URL 或 IP、服务器路径、账号标识、设备唯一标识、客户数据。
- 默认不提交固件二进制、ELF 或 map 文件；记录 artifact 标识、大小和可重建工程即可。
- 不可逆操作（擦除、烧录、写标签、量产、OTA）必须在报告中写明风险与授权范围。
- 原始日志可裁剪噪声，但不得改写会影响结论的字节、错误码或时间顺序。
