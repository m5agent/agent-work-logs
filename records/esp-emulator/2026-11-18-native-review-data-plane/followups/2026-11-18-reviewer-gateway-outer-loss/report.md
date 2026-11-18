# 外层出口网关监督进程退出后的原版审核恢复

先前的具名网关回归验证了外层进程还在时，两套重启的服务如何请求它回收会话。本轮使用相同的原版 CardputerDict 0.6.4、字典种子、受控 Linux QEMU、无外部网卡 VM 以及真实类型化保存快照 dry-run，单独复验外层网关监督进程本身被 SIGKILL 的行为。实验对端使用合成 SNTP，并观测 TCP 内的 TLS ClientHello；未提供证书或外发网络流量。

## 旧版复现

| 旧版 Device Service 1.97.0／Reviewer 0.26.0 | 终止约 10 秒后的观测 |
| --- | --- |
| 只终止外层监督进程，两套服务继续运行 | 旧来宾和内层监督进程已退出，原命名空间无旧进程。命名空间、两端 veth、NAT 表和可写 Flash 仍然存在，旧会话 `stopping` 且持有一个租约。 |
| 终止外层监督进程并终止、重启两套服务 | 旧来宾和内层监督进程仍在，原命名空间有两个进程。命名空间、两端 veth、NAT 表和可写 Flash 仍然存在，旧会话 `stopping` 且持有一个租约。 |

采样前没有人工 Retry 或向旧内层监督进程发信号。两组中断前后的证据均有原版同会话 26 包抓包，抓包和串口对照保留字节前缀。独立网关和实验对端在受测窗口保持可用。完成取证后结束所属隔离 VM。[旧版有界回执](evidence/named-outer-loss-baseline.summary.json)

## 新版和验收边界

恢复逻辑使用与原启动绑定的内层监督进程和内核记录确认网关资源归属。只有能验证同一次 Linux 启动、worker 进程／网络／挂载命名空间、来宾退出和旧命名空间已空时，才自动回收命名空间、虚拟网线和 NAT 表。旧格式记录、启动交接未保存或内层清理无法确认时，旧会话继续等待协调。

Device Service 1.98.0 的实际执行固定在 `dffe87fd60ef34b0c65ddaf7e46ab73fa224d16d`，OpenAPI SHA-256 `bc8340308b18bbe9aaa39990dec65d37c9cd8e9467d5ce4186debd7983a41de9`。Reviewer 保持 `a295e0173a0e3157c120de8ba6fcec128aa665c1` 的 0.26.0。平台套件 2,475 项中 2,465 项通过、10 项跳过，验证器通过。源码也纳入了 Tab5 #188 同原版对照的权威文档。[Device Service 固定源码](https://github.com/m5agent/m5stack-esp-emulator/tree/dffe87fd60ef34b0c65ddaf7e46ab73fa224d16d)

| 新版实际执行 | 首次读取会话详情或执行 Retry 前 | 后续观察 |
| --- | --- | --- |
| 只终止外层监督进程，两套服务继续运行 | 信号后 1.332 秒确认旧来宾、内层监督进程和目标网关的命名空间、两端 veth、NAT 表、可写 Flash 与租约均已释放。 | 保留同会话 26 包抓包，标准 Retry HTTP 202，新会话保存独立的 26 包抓包。 |
| 外层监督进程及两套服务均中断，重启服务 | 约 1.066 秒确认同样资源均已释放，worker 世代推进。 | 保留同会话 26 包抓包，标准 Retry HTTP 202，新会话保存独立的 26 包抓包。 |

两组均核对原启动内外层归属与新旧证据 ZIP 的 CRC 和清单。中断前后原会话抓包均为 26→26，抓包及串口前缀保留。两次标准 Retry 均创建新的同原版会话并通过合成 SNTP 与 TLS ClientHello 观察，综合审核仍为 `manual_review / E_CARDPUTER_PRONUNCIATION_PARTIAL`。独立对端和网关在受测窗口保持，新的测试会话结束后租约为零，实验 VM 均退出。[候选双场景回执](evidence/named-outer-loss-candidate.summary.json)

独立 macOS 原版 Core2 2048 回归也通过。中断置于来宾创建成功后、返回响应前，恢复后保留旧证据和并行会话，正常重试的左、右、上、下棋盘断言均通过，终态 `done / SIM_VERIFIED`。[macOS 原版控制](evidence/macos-core2-control.summary.json)

## 复现

1. 在无外部网卡的 ARM64 Linux VM，用相同原版和存储种子经标准 Reviewer 保存快照 Retry 建立类型化验证会话。准备独立网关对照和本地合成对端。确认实际来宾走到了 SNTP 和 TLS ClientHello，读取活动状态的同会话证据 ZIP。
2. 仅终止属于实验的外层监督进程。一组不重启服务，另一组终止后再启动设备与审核服务。用核对启动归属的只读进程、网络资源和磁盘观察区分旧会话与独立网关。固定采样顺序以区分自动清理和读取接口或标准 Retry 后的清理。
3. 读取中断后的同会话 ZIP，核对 CRC、清单、抓包和串口前缀。确认目标租约与 Flash 的状态，验证同原版标准 Retry 创建的新会话。结束所属进程和 VM，确认独立网关在受测范围内保持。

公网 HTTPS、证书验收、解码发声、实体硬件和浏览器为 **NOT RUN**。未提交 Burner。
