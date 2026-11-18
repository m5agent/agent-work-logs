# Linux arm64 worker 已完成历史的重启恢复

## 固定环境

三个顺序创建的新容器共享同一份独占测试状态，外层网络关闭，无宿主端口映射。前两代保留该实验需要的 namespace 能力，第三代去掉相应能力做负控。两次容器替换均发生在受测 guest 停机后。芯片路径、夹具、QEMU、ROM、容器镜像以及启动程序均在[回执](evidence/linux-worker-idle-restart-summary.json)绑定完整哈希。[Device Service 固定源码](https://github.com/m5agent/m5stack-esp-emulator/tree/13df3b8a7ab197df14f57d2ca8bc58919a7eb666)

| worker 代数 | 先前历史精确读回 | 新执行与准入 | 退出前终态历史 |
| --- | ---: | --- | ---: |
| 1 | 0 单 | 本地 STA 应用 PASS | 1 单 |
| 2 | 1 单 | 本地 STA 应用 PASS | 2 单 |
| 3 | 2 单 | 缺 namespace 能力，HTTP 503，零新分配 | 2 单 |

同一虚拟 guest 的 HTTP POST 和 TCP 二进制双向字节与固定夹具一致，并验证 DNS A、NXDOMAIN、UDP 和最后串口标记。两次读取终态 ZIP 通过 CRC 校验，包内 PCAP 的哈希与独立下载的最终 pcap 一致。每次重启后从服务端读回旧单详情、原保存 ZIP 和 pcap 作逐字节对比。旧单 guest 已停止，Flash 已释放。所有容器都正常清场。

Reviewer 的本地 STA 子断言状态为 PASS，网络外层状态为 PARTIAL。两个无画面 SDK 夹具的整单均为 manual_review，原因 E_NO_FRAME。没有提交 Burner。首次试跑曾复用相同审核任务键，按幂等逻辑返回旧单，夹具编排器拒绝覆盖已存在的目录。保留这次结果，正式队列为每个新审核使用独立键。

## 复现步骤

1. 固定两仓库源码和回执中的 Linux arm64 原生 Xtensa QEMU/ROM，使用同哈希 STA 正控夹具和容器镜像。准备独占的工作目录，把持久的两个服务状态放在可保留的同一测试目录。
2. 使用断开外层网络的容器启动 Device Service 与 Reviewer，授权参数只通过本地测试配置传入。开放验证所需的 Linux network namespace 资源，确认服务公布的对应能力可用。运行带有固定 HTTP POST 与 TCP 收发条件的保存快照 dry-run，校验双向字节、DNS、UDP、串口应答和终态历史。
3. 等 guest 和网络封存完成后读取审核详情和 ZIP，并从 Device Service 读取终态 ZIP 和 pcap。停止两个进程，撤销首个容器。用同一状态目录启动第二个全新容器，证明 worker 世代增加、旧证据精确读回，再用不同任务键运行同一正控并保留终态。
4. 在所有 guest 已停止后再次替换容器，同时去掉 namespace 能力，重复前述读取后发起同一路径的会话创建。核对 HTTP 503、错误码 network_isolation_unavailable、零新租约和两份旧证据均保持。清除自建容器，保留 ZIP 哈希和摘要。

运行中接管、跨主机持久化、常驻发布、真实网络接入和实体设备均为 NOT RUN。测试终止只删除独占容器，未修改已有服务。
