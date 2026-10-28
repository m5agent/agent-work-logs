# ESP Emulator 正式 GitHub Pages 上线报告

## 背景

用户要求把本地 QEMU 修复、远端 CoreS3 C/QEMU WASM 工作台和正式
GitHub Pages 托管一次收口，让用户可以直接访问 `github.io` 测试模拟器。

## 合并与部署

- 远端 WASM 工作台由 PR #16 合并到 main；
- TIMG WDTFEED 修复由 main 提交 `a07f49b7` 收口，GCC 契约可移植性由
  `8e47c6ba` 收口；
- 原仓库 Pages 来源设置为 GitHub Actions；
- main 上以 `publish=true`、`base_path=/m5stack-esp-emulator/` 手动触发
  Pages 工作流；
- 构建 job `13m53s`、部署 job `14s` 均成功；
- 正式地址为 <https://m5agent.github.io/m5stack-esp-emulator/>。

## 公开验收

部署后使用同一真实 C/QEMU 验收器直接访问正式 HTTPS 地址。21 项检查全部
通过：

1. Service Worker 获得控制并启用共享内存；
2. CoreS3 guest ready；
3. runtime、ROM、固件和最终 Flash 身份一致；
4. 实际 320x240 RGB 帧；
5. 触摸负控与正控；
6. PIR 0→1→0 与 QOM 读回；
7. QMP 暂停与继续；
8. 1440/1024/768/390 布局；
9. 停止、分享重开、Worker/iframe 清理；
10. 无服务/本机模拟器请求和 JavaScript 错误。

原始公开验收报告 SHA256：
`3251b33ef5fb76340a48f8cbd3e780ee3b9ce86caf613f176b58a90ffa6bee33`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| review | `PASS` | 本地修复、WASM 分支和公开工作流范围已核对 |
| build | `PASS` | 固定源码 C/QEMU、LittleFS、静态导出与 source archive |
| transport | `PASS` | Pages HTTPS、同源 iframe、串口与 QMP |
| device_response | `PASS` | 实际 CoreS3 guest ready、触摸、PIR 与 QMP |
| data_behavior | `PASS` | 精确 runtime/ROM/固件 SHA、帧像素与输入 |
| visual_or_physical | `PARTIAL` | 浏览器真实 RGB 帧 PASS；物理显示/声学/电气 NOT RUN |
| delivery | `PASS` | 正式 URL 可访问，公开 HTTPS 独立复验通过 |

## 验证边界

站点使用 `cores3-wasm-vm-div8`，虚拟时间和 watchdog 到期相对墙钟慢放
8 倍。默认墙钟 LVGL 调度、长期稳定性、持久化、网络、音频、其它
设备/Unit 和任意固件均未闭环。所有结果均为 browser virtual-device
validation，不是物理硬件测量。

## 风险与回滚

Pages 可随时通过禁用来源或重新部署旧 main 提交回滚；工作流只在显式
`publish=true` 且 `main` 上发布。源码 Git 不包含 ROM、固件、WASM 或依赖
归档。没有执行物理烧录、擦除或其它不可逆设备操作。
