# AIFlow #6「Run Always」资源同步路径重复

- 日期：`2026-11-23`
- 结果：`PARTIAL`（虚拟设备复现；云端真实上传与实体设备 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/AIFlow/issues/6
- 源码版本：`m5stack/AIFlow @ 0bc08aa8442c40c7430f55a37dfa4fab8914d8bf`；UIFlow2 `m5things`/`m5sync` 取自 AIFlow StickS3 固件
- 环境：macOS 主机 + 本机 Device Service + QEMU StickS3（`sticks3`，simulated/display）

## 结论

路径确实错了。`Run Always` 上传应用文件时，AIFlow 客户端把目标写成完整文件路径
`apps/<name>.py`（`filePaths` 字段）。云端固件下发链路把该值当作目录，再补一个文件名，设备端
`m5things` 用 `sprintf("%s%s", devicePath, name)` 直接拼接，最终得到
`apps/<name>.py/<name>.py`。`m5sync` 按 `devicePath` 原样打开文件，父目录
`/flash/apps/<name>.py/` 不存在，稳定返回 `ENOENT`，重试 3 次后显示 `Failed`。

在虚拟 StickS3 上用 AIFlow 固件复现：同一份 `devicePath` 产生 `ENOENT` 并停在 `Failed 50%`；
仅把 `devicePath` 改为 `apps/<name>.py` 后同一路径逻辑下载并校验成功，显示 `Success 100%`。

## 关键证据

- 重复路径串口：`evidence/2026-11-23-serial-duplicated-path.txt`
  - `[WARN] Download error: [Errno 2] ENOENT` 连续 3 次
  - `[INFO] Failed to download file: apps/My_Project_1795168094430.py/My_Project_1795168094430.py`
- 修正路径串口：`evidence/2026-11-23-serial-corrected-path.txt`
  - `[INFO] Downloaded and verified file: apps/My_Project_1795168094430.py`
- 画面：`evidence/2026-11-23-failed-50.png`（135x240，`Failed 50%`）
- 画面：`evidence/2026-11-23-success-100.png`（135x240，`Success 100%`）

## 文件

- `report.md`：完整报告、代码位置与影响面
- `run.json`：结构化记录
- `evidence/`：串口摘录与两帧画面
- `code/repro_sync_path.py`：在 AIFlow StickS3 来宾内运行的最小复现脚本

## 未覆盖项

- 未使用真实 AIFlow 账号走云端 `upload-resource-batch-and-push`，因此“云端把 `filePaths`
  当目录并补 `/`”是从设备端收到的 `devicePath` 与 `m5things` 拼接实现反推，不是云端代码级直读。
- 未在实体 StickS3 上复验；虚拟设备与实体共用同一份 `m5things`/`m5sync` 路径逻辑。
- 本机固件为 AIFlow 仓库内 `aiflow-sticks3.bin`（构建日期 2026-07-22），不是提问者日志中的
  2026-11-17 固件；日志字符串版本不同，但路径拼接与失败状态一致。
- 未修改 AIFlow 或 UIFlow2 仓库，未提交修复。
