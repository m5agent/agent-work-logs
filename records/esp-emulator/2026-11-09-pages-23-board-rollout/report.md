# Pages 下载回退与发布验证

正式站点原部署为 `5f15d1f824958829f7d62648a5efbfe5fcee2edb`，开放 19 款设备。用户批准发布包含初代 Cardputer、PaperS3、PaperDIY、CoreMatrix 和 #211 工作台状态与双 SHA 的主线版本。第一次正式任务从 `02c046679fd7c7dbb008afd3c4c29e3cfca517df` 启动，libffi 归档请求返回 HTTP 403。日志未记录响应头或响应正文，无法确认 403 的进一步原因。

`0ea7e36ae0dd769deb8bf83529756db5e9213e8e` 只修改发布工作流的归档传输。三个原锁定文件逐一验证大小和 SHA-256，构建器仍按各自源码锁独立复核。下载测试通过官方地址完成。模拟主地址返回正确大小但错误内容、鉴权 API 返回 403 时，验证拒绝坏文件并用匿名 API 取回同一归档。重跑的托管下载步骤通过，当前正在按原门禁构建和验收。

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| transport | PASS | 三个官方归档匹配 Xtensa 与 C61 锁，错误内容和 403 回退负控通过 |
| build | PARTIAL | 静态导出和发布契约 10 项通过，托管源构建未完成 |
| virtual-device validation | PASS | 独立导出上 StickC Plus 编辑器 63/63，通过应用显示、硬复位和五个 Worker 回收 |
| delivery | PARTIAL | 正式站点仍是 19 板旧部署，新任务已启动 |
| hardware validation | NOT RUN | 本次针对浏览器 WASM |

在源码树中以 `publish=true`、项目默认前缀和空服务地址触发 `public-site.yml`。本机复验采用 `build_public_site.py` 的正式导出和 `test_public_uiflow_guest.mjs`，选择 `M5_QEMU_DEVICE=stickc-plus` 及系统 Chrome。托管失败记录与本地通过各自绑定不同执行环境。回滚传输改动可撤销本次工作流提交；当前线上部署由 GitHub Actions 管理。

## 本地全量门禁及独立复验

本地同版全量串行门禁在 AtomS3 编辑器硬复位后失败。复位前执行代码、真实画面和旧控制台取消已通过。新 guest 在访问 SYSTIMER 0x60023008 时出现 Core 1 LoadStorePIFAddrError，未取得新启动就绪标记。同一固件和 WASM 的独立复验通过 63 项，回收全部 Worker。首次失败保留，本地全量结果不作为发布通过依据。 [复验摘要](evidence/local-atoms3-reset-summary.json)

## 新机型定向验证

同一独立导出上，初代 Cardputer、PaperS3、PaperDIY 的固定例程各通过 26 项，CoreMatrix 通过 28 项。另用未修改的 CoreMatrix 官方 UIFlow2 v2.5.4 镜像验证真实 C61 启动、USB REPL、矩阵显示和停止，五个 CDP Worker 目标全部退出。这些是本地定向结果。 [运行摘要](evidence/four-board-fixed-and-c61-stock-summary.json)

## 托管门禁失败

工作流 42597576699 成功构建并导出两套 WASM，CoreMatrix 原版通过。Atom Matrix 编辑器用例在正常 QMP 退出、四个 pthread 全部消失和 iframe 移除后，CDP 仍观察到一个引擎 Worker。72 个计划用例中首个失败，71 个未执行，部署跳过。失败层级为浏览器清场；复位后的真实代码执行已经通过。 [托管工作流](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42597576699) · [脱敏摘要](evidence/hosted-atom-matrix-worker-summary.json)

## 引擎关闭候选

针对两次托管端残留引擎 Worker，提交 f23ecfe8 改用引擎在释放回执、端口关闭和 owner 通知后调用 self.close()。初始化失败和异常仍保留强制回收兜底。验收继续要求独立 CDP 观察到目标实际消失。本地最终导出的 Atom Matrix 58/58 与 StickC Plus 63/63 均通过，两轮各五个 Worker 目标全部退出，兜底终止为零。此前并行诊断在 StickC Plus2 也有自关闭后目标残留的失败，故托管修复效果仍须由串行完整门禁证明。 [本地摘要](evidence/engine-self-close-summary.json) · [正式重跑](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42603482039)

## 第三轮托管门禁及本地触摸复验

工作流 42603482039 两套运行时、导出和 CoreMatrix 原版均通过。Atom Matrix 完成冷启动和复位前代码检查，QMP 硬复位进入新控制台周期。新客体串口到 bootloader 入口与 I²C 初始化报错后停滞，600 秒内未发出第二次就绪标记。I²C 是最后观察到的日志，尚不足以定位复位根因。失败清场有正常退出码和自关闭通知，Chrome CDP 仍记录一个引擎 Worker。正式部署跳过。 [托管重跑](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42603482039) · [运行摘要](evidence/hosted-self-close-reset-summary.json)

本地完整门禁另在 PaperS3 触摸失败。同镜像独立重跑复现，等待客体出现稳定轮询后，同样 250 毫秒输入得到实际按下、松开、坐标和清场通过。该验证为定向诊断，未代替正式全量门禁。 [PaperS3 摘要](evidence/local-papers3-touch-cadence-summary.json)

## 2026-11-10：Atom Matrix 同会话复位基线

在未改动的 f23ecfe8 浏览器运行时上，用 Chrome 157.0.8103.39、本地独立静态导出和同一固件执行标准编辑器用例，追加八次交替的运行中与空闲硬复位。九次均取得 QMP RESET、新控制台周期、新的 UIFlow 就绪标记和该周期独立的串口输出；共 102 项通过。额外八次从硬复位到新代码回显为 40.25–41.67 秒。正常退出码 0，五个 CDP Worker 目标均消失，强制回收为零。 [脱敏摘要](evidence/local-atom-matrix-reset-stress-summary.json)

本机结果保留原托管失败。托管失败曾于复位约 39.6 秒后额外创建一个嵌套 pthread，此现象未出现在本机九次复位中；尚无证据把它确定为固件复位或引擎目标残留的根因。正式 Pages 仍未更新；未运行真机。

## 2026-11-10：PaperS3 稳定轮询复验

实际客体的一组心跳相隔 1002 客体毫秒，在宿主侧仅相隔 475 毫秒。验证保留原 250 毫秒触摸长度，等待两个独立的客体和宿主心跳间隔均约 1 秒后再送输入。模型实际按住 253.97 毫秒，GT911 客体报告 (270,400) 按下与松开；10 项检查通过，6 个 CDP Worker 目标均退出。该改动只触及 PaperS3 测试前置观察，PaperDIY 不继承。 [脱敏摘要](evidence/local-papers3-fresh-polling-summary.json)
