# StackChan 稀疏舵机状态展示平滑与 Pages 发布

- 日期：`2026-10-31`
- 结果：`PASS`（browser-WASM、public HTTPS 与交付均验证；物理硬件 `NOT RUN`）
- 工作类型：`code_change` + `service_debug`
- 问题来源：用户反馈 StackChan 舞蹈 demo 已能运动但看起来卡顿，要求修复并部署新网页
- 源码版本：`m5stack-esp-emulator @ 948ca8b5`，合并 `68afbd7c`
- 固件：完整 Flash SHA-256 `c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542`

## 结论

原始 SCS `present_position` 仍然是稀疏 QOM 采样。页面现在只对 3D 展示按相邻
样本的墙钟间隔做最多 `1.2 s` 的插值，不增加或改写 guest 采样、角度标签、
DOM ticks、串口及 evidence。

同一完整 Flash 在 Metal 硬件渲染下独立运行两次，均为 `12/12 PASS`：

- 每次 23 个原始状态、30 个有效 SCS 包；
- 2 秒窗口分别输出 15 / 14 个中间 3D 姿态；
- 最大单帧视觉步进约 `9.03° / 9.34°`，而不是修复前直接采样跳变的最大约 `86.9°`；
- 正常 Stop 后 engine 与五个 pthread target 在浏览器上下文关闭前实际消失。

正式站点已发布 manifest `22b90111ae80080ea5b7e9e73ae140af758a4ef60cfb4bd3286c0b61d4be4ae8`。
正式 HTTPS 地址在 macOS M4 / ANGLE Metal 下完成真实 CoreS3 guest `30/30`，
包含 COI、LVGL 帧、触摸、PIR、QMP pause/resume、分享重开和两代 12 Worker 清理。

## 关键证据

- `evidence/browser-smoothing.md`：两次精确固件运行及视觉中间姿态
- `evidence/cleanup.md`：engine handle finalize 与两代 Worker target 关闭
- `evidence/pages-deployment.md`：release、manifest、线上哈希和公开 HTTPS 验收
- `evidence/native-service.md`：`/api/v1` 虚拟烧录、串口与画面

## 文件

- `report.md`：完整根因、实现、验证与边界
- `run.json`：结构化记录
- `evidence/`：上述证据
- `patches/`：不适用；代码通过 PR #71/#72 交付
- `code/`：仓库内现成 Node browser-WASM harness

## 未覆盖项

- 插值只改善浏览器显示，不证明物理舵机连续运动、机械速度、扭矩或电气行为。
- 物理 StackChan、LCD 光学、音频与 RF 均为 `NOT RUN`。
- regular source-build Pages workflow 两次因上游依赖 TLS 超时未进入浏览器验收；
  prepared-site 发布已成功，但该工作流本身保持独立 `PARTIAL`。
