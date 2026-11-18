# Core2 2048 的保存快照四向回归

工作环境为 macOS 原生 Core2 QEMU，固定 Device Service 1.99.0 源码 `9837c3f84df4383eb74881a1f44fcd3f460daefa`，Reviewer 0.28.0 源码 `37d7675dced42b2b932c51d1ca21bbb8ccfdf7e1`。两项服务均在独立本地状态目录运行。原版 2048 Game 1.0 应用镜像的 SHA-256 为 `41db3680f167565dc3ba06e30493e5bb9d6985ee2c5c9e7706940d003a1fdcaa`，组合后的可启动 Flash SHA-256 为 `cd13c9bc7594ea3ad1994b1192d7bdd620ab1e6fa2adb2abf23152ebd80020d8`。

## 复现

1. 准备标准可重试的保存快照，校验原版 SHA-256 与长度。使用 `POST /api/reviews/{id}/retry`，设定 `sourceMode=saved_snapshot`、`useAgentReview=false`、`validation.core2_2048_moves=true`，提供 [本轮拖动坐标与方向](evidence/core2-2048-review028.summary.json)。
2. 先将 `validation.input_assertions` 设为非结构化数值进行拒绝对照。审核返回 HTTP 400，任务状态与事件不变，worker 仍为零租约。用原计划重试后只创建一个原版 Core2 会话。
3. 取得欢迎棋盘后，按右、左、上、下顺序发出两轮拖动。在同一运行中持续比较移动前、动作后首次与稳定帧。独立从实际 320×240 帧读取 4×4 棋盘，计算该方向的挤压及合并。每步观察与预测仅差一个原本空格上的新增 2 或 4。
4. 在停机前导出证据 ZIP。核对会话清单、所有成员的哈希与 CRC，在保留的 Flash 副本验证工厂应用完整。停机后确认运行中的可写 Flash 与租约已释放、原生程序与工作器退出。

## 结果与边界

| 方向 | 两轮合计 | 观察 |
| --- | --- | --- |
| 右 | 2/2 | 棋盘按向右挤压及合并后新增一个有效方块 |
| 左 | 2/2 | 棋盘按向左挤压及合并后新增一个有效方块 |
| 上 | 2/2 | 棋盘按向上挤压及合并后新增一个有效方块 |
| 下 | 2/2 | 棋盘按向下挤压及合并后新增一个有效方块 |

八步均被输入接口接受，四向合法移动和帧变化均通过。保留的证据 ZIP 固定同一次 Core2 会话与实际文件哈希，停机回执独立验证清理。摘要省去会话标识、服务端点、路径及原始镜像与帧数据。

本次验证限于原版与此原生虚拟设备流程。物理触摸、浏览器 WASM、生产来宾和 Burner 提交未执行。 [上一版回归](../../report.md) · [固定 API](https://github.com/m5agent/m5stack-esp-emulator/blob/9837c3f84df4383eb74881a1f44fcd3f460daefa/docs/device-service-api.md)
