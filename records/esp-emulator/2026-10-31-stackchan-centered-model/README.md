# ESP Emulator 同步 StackChan 居中显示模型

- 日期：`2026-10-31`
- 结果：`PASS`（virtual-device、浏览器模型与公开 Pages 已验证；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 问题来源：用户要求同步公开仓库 `yuyun2000/m5stack-models` 刚更新的 StackChan 模型
- 源码版本：`m5agent/m5stack-esp-emulator @ a8b61e2b`，PR #74 合并 `929723b0`
- 模型源：`yuyun2000/m5stack-models @ 1373680d29667f99438a5412b87b955a3ba7702f`
- 环境：macOS M4、Chrome、ANGLE Metal、browser-QEMU、GitHub Pages

## 结论

模拟器已从上一固定版本 `4879ab51` 同步到上游 `1373680d`。本次运行时变更只有
StackChan 屏幕居中：`CoreS3.build()` 接受 `lcdCenterY`，StackChan 以
`lcdCenterY: 0` 构造内部 CoreS3，使 LCD backing 与可见 Display 都位于方形头部中心。
上游新增的浏览器截图、计划文档和 Pages workflow 没有被 vendor 同步脚本带入运行时。

同步后的静态站点使用完整 StackChan 舞蹈固件通过 `12/12` browser-QEMU 检查；
正式 Pages 已部署，线上 manifest/WASM/vendor manifest 与本地验收导出一致。
线上页面加载 StackChan 模型后无 JavaScript 错误，LCD 本地坐标为
`[0, 0, 7.81]`，世界坐标为 `[0, 8.25, 30.81]`。

## 关键证据

- `evidence/sync-and-contracts.json`：固定源、同步文件、1,925 文件闭包和平台测试结果
- `evidence/stackchan-browser-validation.json`：同固件舞蹈、SCS、帧和清理结果
- `evidence/pages-deployment.md`：release、workflow、公开哈希与线上模型回读
- `evidence/stackchan-live.png`：正式 HTTPS 页面加载新模型的截图

## 文件

- `report.md`：同步范围、执行命令、验证和边界
- `run.json`：结构化记录
- `evidence/`：上述摘要与截图
- `patches/`：不适用；上游 runtime 文件由受审同步脚本生成
- `code/`：仓库内 `sync_visual_models.py` 与 browser-QEMU harness

## 未覆盖项

- 物理 StackChan、LCD 光学、机械、电气和 RF 行为均为 `NOT RUN`。
- 本次没有用 regular source-build Pages workflow 重建 C/QEMU；正式页面通过已发布的
  prepared-site workflow 部署。prepared artifact 来自本次源码导出的静态站点并在部署后回读校验。
