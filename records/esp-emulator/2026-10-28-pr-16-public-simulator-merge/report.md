# PR #16 CoreS3 C/QEMU 浏览器工作台合并报告

## 背景

- 来源：[PR #16](https://github.com/m5agent/m5stack-esp-emulator/pull/16)
- 需求：合并 CoreS3 C/QEMU WASM 浏览器工作台、视觉模型更新和
  GitHub Pages 导出/验收入口。
- 目标：在不覆盖本地未提交 Core2 WDT 诊断的前提下解决冲突、独立验证
  网页执行路径并更新 main。

## 结论

- 状态：`PASS`
- 合并方式：从最新 main 创建独立合并 worktree，再合并 PR head
  `81d44d89`；没有触碰原 worktree 的未提交文件。
- 冲突：仅 `docs/project-snapshot.md`。该文件是生成物，冲突后用
  `platform/tools/project_snapshot.py --write` 按合并树重新生成。
- 交付：merge commit `ef5f6d79` 已推送到
  `m5agent/m5stack-esp-emulator` 的 main；PR 状态为 `MERGED`。

## 独立验证

### 静态工作台

使用合并树导出 source-only 公开站点，并以本地静态服务器执行真实
Chromium 页面检查。结果为 `PUBLIC_WORKBENCH_BROWSER_OK 16 checks`，
覆盖页面导航、设备筛选、模型显示、服务连接拦截、错误恢复和响应式布局。

### 公开 Pages 实际 CoreS3 客体

验收器先逐字节绑定公开站点的执行文件和 runtime manifest，再启动真实
C/QEMU CoreS3 客体。21 项检查全部通过：

- Service Worker 启用共享内存；
- 真实 320x240 LVGL 帧和精确固件身份；
- 无效触摸不触发、有效触摸触发客体回调；
- PIR 的 0→1→0 状态与 QOM 读数一致；
- QMP 暂停阻止客体继续输出，继续后恢复；
- 1440/1024/768/390 四档布局无水平溢出；
- 停止后退出码 0、无残留 Worker/iframe；
- 分享链接创建新客体并完成干净停止；
- 全程无 JavaScript 错误，也未访问 `/api/v1` 或本机模拟器接口。

这是 `browser virtual-device validation`，不是物理硬件验证。

### 平台与契约

- Python 平台套件：`1391` 项，`1390 PASS + 8 skipped + 1 error`。
- 唯一错误：macOS multicast loopback 的匿名 discovery beacon 超时；
  `test_worker_discovery.py` 和 `worker_discovery.py` 与 main 完全一致，
  不由 PR #16 修改。Linux CI 的 `network-namespace-policy` 已通过。
- `qemu_profiles`、`peripheral_catalog`、`runtime_coverage` 和
  `project_snapshot --check`：全部通过。
- Python compileall：通过。
- Node `test:contracts`：全部通过。
- PR CI：`platform-contracts` 与 `network-namespace-policy` 均成功。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| review | `PASS` | 739 文件、86,443 行新增的 PR 范围与合并冲突已检查 |
| build | `PASS` | 固定源码的公开 C/QEMU WASM/ROM/Firmware 身份校验 |
| transport | `PASS` | 同源 iframe 控制通道、串口和 QMP 暂停/继续 |
| device_response | `PASS` | 实际 CoreS3 客体 ready、触摸回调和 PIR 双向状态 |
| data_behavior | `PASS` | 精确固件/WASM/ROM SHA、帧像素、输入与退出状态 |
| visual_or_physical | `PARTIAL` | 浏览器内真实 RGB565 帧 PASS；物理屏、声学和电气 `NOT RUN` |
| delivery | `PASS` | main 已更新，PR #16 已标记为 merged |

## 验证边界

本轮不证明物理硬件、RF、电气、声学或光学行为。C/QEMU 为
`cores3-wasm-vm-div8` 研究原型，虚拟时间与看门狗到期按 1/8 慢放。
未验证默认墙钟调度、长期稳定性、Flash 持久化、网络、音频、其它设备、
其它 Unit 或任意固件兼容性。

## 风险与回滚

合并把 739 个文件、大量视觉模型资产和 QEMU WASM 补丁带入 main，仓库体积
会明显增加；源码 Git 不包含 ROM、固件、WASM 或依赖归档。回滚方式是
revert merge commit `ef5f6d79`。没有对物理设备执行烧录、擦除或其它不可逆操作。
