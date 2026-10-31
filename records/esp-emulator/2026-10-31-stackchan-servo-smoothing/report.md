# StackChan 稀疏舵机状态展示平滑报告

## 背景

用户已能运行 StackChan 舞蹈固件，但 3D 机器人动作呈明显跳变，询问是电脑性能
还是采样问题，并要求修复后部署新网页。

此前对照显示，关闭整帧抓取和切换 GPU 后端都没有把 30 个 SCS 位置包变成更密集
的 guest 输出。真正的表现问题是每个稀疏 QOM 快照都被 `durationMs: 0` 直接
应用到 3D 关节。

## 实现

1. `qemuServoVisualCommands()` 接受经过校验的可选展示时长。
2. `public.js` 对每个 StackChan 状态记录到达时间，以相邻样本间隔的 90% 计算
   展示过渡，限制在 `80..1200 ms`；packet 回退时不做插值。
3. 原始 present position、DOM ticks、角度标签和 evidence 仍使用采样值。
4. owner 收到 engine close 通知后终止 Worker handle，并在新任务中再次终止；
   runtime 在删除 iframe 前保留 250 ms，让 finalize 任务先完成。

## 验证

### 精确固件 browser-WASM

固定完整 Flash：

```text
c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542
```

固定 WASM：

```text
5d6c36bdafc1129c2652b5ba9422f3deb5ab170475748cea96fdc4cf9520a993
```

两次独立 Metal 运行：

| 运行 | 检查 | 原始状态 | 帧 | SCS 包 | 2 秒中间姿态 | 最大视觉步进 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 12/12 PASS | 23 | 615 | 30 | 15 | 9.03° |
| 2 | 12/12 PASS | 23 | 546 | 30 | 14 | 9.34° |

两次均保持 yaw `307..613`、pitch `677..850` 和 DOM/packet 同步。

### 原生 Device Service 回验

通过代理自有端口和独立 state 目录调用 `/api/v1`：

- artifact/firmware SHA 与输入完整 Flash 一致；
- 串口出现 `SERVO ready`、`StackChan auto-dance started` 和连续 cue；
- session 进入 `running`，保留 `320x240` 非空画面与 evidence ZIP；
- 以 `purge=0` 停止并确认 terminal history。

该原生构建不暴露 `/machine/scs_servo`，所以关节展示结果只引用匹配的
browser-WASM harness，不把 native 结果拼接成 SCS 观察。

### Pages

- 正式地址：<https://m5agent.github.io/m5stack-esp-emulator/>
- release：`pages-preview-20261031-stackchan-smoothing`
- release asset：`151913554` B，
  SHA256 `1565afc97085cfa4f33760bf7655d9d19d43897f742f1615fca57dda62be2e5a`
- 部署运行：`41158906682`，prepare/deploy PASS
- manifest：`22b90111ae80080ea5b7e9e73ae140af758a4ef60cfb4bd3286c0b61d4be4ae8`

从正式 HTTPS 重新加载当前 manifest、脚本和完整 WASM，哈希与待部署导出一致。
真实 CoreS3 guest 验收 `30/30`，两代 engine/10 pthread target 均在上下文关闭前
实际消失。

## 验证边界

- 这是 virtual-device / browser-WASM 验证。
- 展示插值没有增加 guest 采样，不能用来推断真实舵机速度、扭矩、机械行程或电气行为。
- regular source-build Pages workflow 两次失败在构建机下载依赖的 TLS 阶段：
  `The handshake operation timed out`。该失败与本次代码和 guest 验收分开保留。

## 回滚

- 网页可回退到上一 prepared-site release。
- 页面内的 QOM/角度证据仍保留原始采样；关闭插值只需恢复
  `qemuServoVisualCommands(..., 0)`。
