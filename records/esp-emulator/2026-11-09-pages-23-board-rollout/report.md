# Pages 下载回退与发布验证

正式站点原部署为 `5f15d1f824958829f7d62648a5efbfe5fcee2edb`，开放 19 款设备。用户批准发布包含初代 Cardputer、PaperS3、PaperDIY、CoreMatrix 和 #211 工作台状态与双 SHA 的主线版本。第一次正式任务从 `02c046679fd7c7dbb008afd3c4c29e3cfca517df` 启动，libffi 归档请求返回 HTTP 403。日志未记录响应头或响应正文，无法确认 403 的进一步原因。

`0ea7e36ae0dd769deb8bf83529756db5e9213e8e` 只修改发布工作流的归档传输。三个原锁定文件逐一验证大小和 SHA-256，构建器仍按各自源码锁独立复核。下载测试通过官方地址完成。模拟主地址返回正确大小但错误内容、鉴权 API 返回 403 时，验证拒绝坏文件并用匿名 API 取回同一归档。重跑的托管下载步骤通过，当前正在按原门禁构建和验收。

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| transport | PASS | 三个官方归档匹配 Xtensa 与 C61 锁，错误内容和 403 回退负控通过 |
| build | PARTIAL | 静态导出和发布契约 10 项通过，托管源构建未完成 |
| virtual-device validation | PASS | 独立导出上 StickC Plus 编辑器 63/63，通过应用显示、硬复位和六个 Worker 回收 |
| delivery | PARTIAL | 正式站点仍是 19 板旧部署，新任务已启动 |
| hardware validation | NOT RUN | 本次针对浏览器 WASM |

在源码树中以 `publish=true`、项目默认前缀和空服务地址触发 `public-site.yml`。本机复验采用 `build_public_site.py` 的正式导出和 `test_public_uiflow_guest.mjs`，选择 `M5_QEMU_DEVICE=stickc-plus` 及系统 Chrome。托管失败记录与本地通过各自绑定不同执行环境。回滚传输改动可撤销本次工作流提交；当前线上部署由 GitHub Actions 管理。

## 本地全量门禁及独立复验

本地同版全量串行门禁在 AtomS3 编辑器硬复位后失败。复位前执行代码、真实画面和旧控制台取消已通过。新 guest 在访问 SYSTIMER 0x60023008 时出现 Core 1 LoadStorePIFAddrError，未取得新启动就绪标记。同一固件和 WASM 的独立复验通过 63 项，回收全部 Worker。首次失败保留，本地全量结果不作为发布通过依据。 [复验摘要](evidence/local-atoms3-reset-summary.json)

## 新机型定向验证

同一独立导出上，初代 Cardputer、PaperS3、PaperDIY 的固定例程各通过 26 项，CoreMatrix 通过 28 项。另用未修改的 CoreMatrix 官方 UIFlow2 v2.5.4 镜像验证真实 C61 启动、USB REPL、矩阵显示和停止，五个 CDP Worker 目标全部退出。这些是本地定向结果。 [运行摘要](evidence/four-board-fixed-and-c61-stock-summary.json)
