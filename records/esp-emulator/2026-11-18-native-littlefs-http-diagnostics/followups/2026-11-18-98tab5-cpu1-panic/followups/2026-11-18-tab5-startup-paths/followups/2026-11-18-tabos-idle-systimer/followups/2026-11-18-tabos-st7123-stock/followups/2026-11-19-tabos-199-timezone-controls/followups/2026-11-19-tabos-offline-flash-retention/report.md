# M5TabOS 原版的离线设置和虚拟 Flash

## 基线和改动

使用同一份 M5TabOS 0.9.1 原版、同一规范化 Flash、`esp-emu 1.1.0`、ST7123 Part、P4 ROM、eFuse 和 C6 镜像。两个测试工人各用独立状态和一个会话，复用先前校验过的只读固件库存。运行的候选 Python 文件来自已提交的 `76e734f5cf061bc7985a1bf6146f2cb5de223023`，逐一按源码核验。通过标准 `serve.py` 启动，没有诊断钩子、ELF 或来宾代码修改。API 的精确版本和产物摘要见 [运行记录](run.json)。

旧版将本次会话的 Flash 镜像交给 P4 模拟器。复位时停止 P4 和 C6 后重新拉起，旧版没有请原生 P4 在退出时回写 Flash。`76e734f5` 只对哈希已准入的 P4 DSI 运行路径启用 `--save-state`，且要求 Flash 为会话内普通、单链接的正确大小文件。C6 启动参数保持无 `--save-state`。源码在有回写能力的 P4 未正常结束时拒绝重新启动，以免把未保存的状态当成成功复位。

## 复现

1. 冷启动 `tab5 / qemu` 普通 Device Service 会话并确认 ST7123 与原生 DSI，不设置匹配 ELF。使用 720×1280 `panel` 坐标和 `/sessions/{id}/frame.png?max_age_ms=0&orient=panel` 读取实时画面。
2. 点击欢迎页 `PRÓXIMO` (530, 1147)，点击时区 +30 分 (606, 365) 将 `UTC-3:00` 改成 `UTC-2:30`。按同一 `PRÓXIMO` 到 Mesh 页面，选择 `Não usar a internet` (376, 585)，再进入 Wi-Fi 页面并直接点击 `CONCLUIR` (536, 1145)。每次 ST7123 输入都有按下与释放两条确认。
3. 在首页点击 `Ajustes` (448, 313)。核对 `Data e hora` 的 UTC 偏移和 Wi-Fi `Desligado`。进入 `Malha pela internet` (655, 535) 核对状态 `Desligada`。此页的 `Automático` 表示服务器预设。
4. 调用 `POST /api/v1/sessions/{id}/reset`。核对回执仍是同一会话、原 P4/C6 进程退出、新进程运行。独立读取复位后首页、实际点击进入设置及 Mesh 子页。对照回看会话独立的 24 KiB NVS。
5. 候选复位后再次进入 `Data e hora` (650, 1123)，点击加号 (514, 413) 写入 `UTC-2:00`。调用 `DELETE /api/v1/sessions/{id}?purge=0&retain_flash=1` 后，使用 `GET /api/v1/sessions/{id}/flash?format=bin` 读回 16 MiB，只在私有证据保留 NVS 切片。重新请求停机释放可写 Flash。

## 结果

| 路径 | 复位后画面 | Flash 读回 |
| --- | --- | --- |
| 1.99.0 `9837c3f8` | 欢迎页 PNG 与首次冷启动全图相同 | NVS 为原版空白，零变更字节 |
| 1.99.1 `76e734f5` | 直接进入 `Início`，重新点击实际显示 `UTC-2:30`、Wi-Fi `Desligado`、Mesh `Desligada` | 相对原始 NVS 有 910 处变化。一页和 12 个条目校验通过，带符号字段与界面设定相同 |
| 1.99.1 正常停机保留 | 来宾停机前设置页显示 `UTC-2:00` | 停机导出与本地同会话镜像相同。NVS 相对前次改 25 字节，同一带符号字段为新偏移。应用 Flash 区逐字节不变 |

复位前后设置页的全图 SHA 相同，Mesh 子页全图 SHA 也相同。原 BIN、库存规范化 Flash、原生可执行文件和 C6 seed 均通过停机前后哈希对照。各次证据 ZIP 的 CRC、成员哈希和会话源身份已复核。最后两种设备进程均退出，活动租约为零，可写 Flash 已释放。公开摘要省去端点、会话标识和 NVS 键名。原始截图、ZIP 和 Flash 切片只在私有取证区留存。

回滚服务代码可撤回 `76e734f5` 的 P4 回写和复位判定，当前有缺口的基线足以说明这会重新丢失复位时的原版设置。未执行真实联网、真机、浏览器或其它应用覆盖。未提交 Burner。
