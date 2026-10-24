# ESP Emulator worker control/runtime plane split report

## 背景

原有 `WorkerAgent` 使用一个 `--service-url` 完成中央队列控制和 QEMU session
执行。因此所谓 worker executor 仍由中央 Device Service 启动 QEMU，不能
表达“中央控制面 + worker 本地执行面”的跨主机拓扑。

目标是把 job ownership 与 QEMU ownership 分离，同时保持原同主机命令兼容。

## 结论

- `WorkerAgent` 新增可选 `runtime_api`。
- claim、worker heartbeat、job heartbeat 和 terminal result 固定在 control
  API。
- session create、running wait、evidence 下载和 `DELETE ?purge=0` 固定在
  runtime API。
- result summary 记录 `execution_plane=worker-local` 或
  `control-service`。
- CLI 新增 `--runtime-service-url`；
  `M5_RUNTIME_SERVICE_URL` 与该参数等价。
- `--runtime-token` / `M5_RUNTIME_SERVICE_API_TOKEN` 可为 runtime API
  使用独立 token；未设置时复用 control token。
- control/runtime URL scheme 必须一致，单套 TLS client context 可同时用于
  两个 HTTPS 端点。
- credential generation reload 在 runtime token 未单独指定时同步更新 control
  和 runtime API。

## 验证

### 单元契约

两个独立 fake API 分别记录请求：

- control API 只收到 worker/job claim、heartbeat 和 result；
- runtime API 收到 session create、running、evidence 和 stop；
- result state 为 `PASS`，evidence SHA256 来自 runtime plane；
- CLI 正确解析两个 URL。

### Linux namespace

在 privileged Linux container 中运行拆分后的 no-QEMU fixture：

```bash
python3 tests/network/worker_cross_netns/run_test.py \
  --out-dir <private-output-dir>
```

结果为 `13/13 PASS`：veth route、实名 registration、submit/claim、
worker/job heartbeat、terminal result、worker stop、无 QEMU、无 device
session、namespace cleanup 和 token 不落日志全部成立。

### 平台回归

```text
350/350 platform tests PASS
runtime coverage PASS
peripheral catalog PASS
QEMU profiles PASS
project snapshot PASS
Ruff fatal / F401 / F841 PASS
compileall PASS
```

## 新 fixture 设计

`tests/network/worker_cross_netns/run_test.py --qemu --firmware ...` 会：

1. 在 server namespace 启动中央 Device Service；
2. 在 worker namespace 启动独立 Device Service；
3. worker 将完整 StickS3 flash 上传到本地 runtime；
4. worker 向中央队列提交 job；
5. worker 从中央队列 claim，在本地 runtime 创建 QEMU session；
6. 下载 evidence，停止 session；
7. 验证 manifest/serial、QEMU reap、token 脱敏和 namespace cleanup。

该模式代码已提交，但本轮没有执行，不能标记为 `PASS`。

## 验证边界

- Linux namespace 不是物理独立主机。
- no-QEMU control-plane smoke 不等于 worker-local QEMU executor。
- 未验证首帧、应用输入、companion HTTP/BLE、evidence-stream continuity 和
  跨 worker 进程 reattach。
- 没有真机、RF、功率或电气结论。

## 风险与回滚

启动真实 `--qemu` fixture 会额外运行一个 QEMU，应在设备 soak 结束后执行，
避免 CPU/内存竞争污染证据。回滚目标为源码提交
`261d31016aedd85974ad15a46e3b413c2a8f2bcf` 的反向提交。
