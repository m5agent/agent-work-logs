# 创建请求跨 Reviewer 崩溃边界的实际复验

## 原因和改变

Reviewer 可能在设备服务已接收创建之后、保存响应之前退出。恢复时需要区分请求已分配与尚未分配，避免既有会话泄漏和延迟到达的重复创建。新实现先把与请求绑定的待处理记录写入持久数据库，再发送创建；重启后与同一个 Device Service worker 协调已创建或未创建状态。已创建的目标以保留证据模式停止，未创建的目标将旧请求封存。核对未完成时重试暂不准入。旧版本边界用独立执行记录保留。

冻结所用 Device Service 1.95.0 源码为 [`5b4b664272cab0a419257327baf42b26b12d79f6`](https://github.com/m5agent/m5stack-esp-emulator/tree/5b4b664272cab0a419257327baf42b26b12d79f6)，OpenAPI SHA-256 为 `900f9734795148a0fc28dc5ff494177041933db88d9b01a79e4484fee002736f`。Reviewer 0.25.0 源码固定在 `0f732ea5c62596c0137e8ca0cd3a32e7aa3c3988`，OpenAPI SHA-256 为 `8894feba45bd97070953689170ce3d8700d1e177b94ff9b40f5a222884b1583c`。Device Service 完整测试收集 2,454 项（2,444 通过、10 跳过），Reviewer 288 项通过。软件测试与实际来宾结果分别记录。

## macOS 原版 Core2 开发验证

使用 Core2 2048 Game 1.0 原版应用 SHA-256 `41db3680f167565dc3ba06e30493e5bb9d6985ee2c5c9e7706940d003a1fdcaa`，具备已固定的应用匹配启动上下文。导入后 Flash SHA-256 为 `cd13c9bc7594ea3ad1994b1192d7bdd620ab1e6fa2adb2abf23152ebd80020d8`。原生 Xtensa 运行时 SHA-256 `38549673557129d5e9e0100ce9de6539b261b834e9960523b2400dfa110c61b5`。

| 独立关口 | 验收观测 |
| --- | --- |
| Device Service 已创建，Reviewer 尚未收到响应 | 配置对照代理扣住成功响应，现场确认有实际原版来宾和独立来宾运行；SIGKILL Reviewer，重启同一数据库。恢复命中已分配目标，释放该租约与 Flash，停止后旧 ZIP 串口仍包含此前已读字节。 |
| Reviewer 请求尚未送达 Device Service | 对照代理扣住原 HTTP 创建。SIGKILL 并重启后协调返回 `not_created`。再转发完全相同的原请求，得到 `409 session_create_reconciled`，始终零新会话和租约。 |
| 已分配关口的正常重试 | 标准保存快照 Retry 新建独立会话，实际原版左右上下均完成合法板面移动，终态 `done / SIM_VERIFIED`。无关来宾在恢复和重试前后均保留原进程和租约。 |

两次在 SIGKILL 前核对持久记录中的请求哈希确实绑定已扣住的请求，重启后均核对同一 worker 身份。两次最终均释放所属租约并退出服务与代理。已保存和停止后读取的旧证据、重试证据 ZIP 与同会话来源均已核验。第一轮的本地复验工具曾在构造隔离数据副本、所有者字段读取及 SQLite 数值判定处提前中断。上述终态来自修正复验工具后重新执行的两个独立会话。[有界 macOS 回执](evidence/macos-create-recovery.summary.json)

## Linux 活跃网络会话 A/B

两组均在无外部网卡的 ARM64 Linux 虚拟机使用同一份 Cardputer ADV STA SDK 固件，所用 SHA-256 为 `a225471a938cd2ffef45b555f6518e485be9c09566fdb4235048962b7bfea2fd`。运行时为 Linux ELF QEMU `1733f511c4528cbd991e673069ecedf261b7043e8302553e050924089ce09bff`，ROM 为 `b5c7090cc22efce51c1323cef31ca96fcd673a5b1d1b1017e219d393f2659913`。每组均用保存快照的标准 Retry 请求启动一个独立网络命名空间内的来宾，仅关闭并重启 Reviewer，Device Service 进程和 worker 世代不变。

| 时序 | Device Service 1.94 / Reviewer 0.24 | Device Service 1.95 / Reviewer 0.25 |
| --- | --- | --- |
| Reviewer 重启后、人工清理前 | 旧来宾和网络监督进程仍运行，剩 1 个租约。 | 旧会话停止，来宾和网络监督进程均退出，剩 0 个租约。 |
| 同会话抓包、串口与证据 ZIP | 活跃抓包 54 包，显式停止后的抓包为 57 包，活跃内容是停止后文件的精确字节前缀。 | 活跃和停止后抓包均为 53 包，字节完全相同。 |
| 标准重试 | 显式回收旧会话后，HTTP 202 创建一个新会话。 | 自动回收后，HTTP 202 创建一个新会话。 |

两组中断任务均如实返回 `service_error / E_SERVICE_RESTART / SIM_PARTIAL`。两组的重试同固件均通过真实 STA 连接、DNS、UDP、HTTP POST 与 TCP 观测，Reviewer 和 Device Service 的证据抓包完全一致。该 Linux 固件无界面，重试的综合审核终态为 `manual_review / E_NO_FRAME`。两组最终均释放 Flash、清零租约并恢复相应命名空间数量，隔离服务均已退出。[有界 Linux A/B 回执](evidence/linux-reviewer-restart-ab.summary.json)

较早的三轮 Linux 环境调试不计入 A/B。首次停在环境依赖准备，一轮在创建前等待超时，另一轮接受一次真实创建后在复验断言处中断。这些不完整尝试没有产生本次来宾重启终态判定。

## 复现

1. 使用固定版本代码和公开原版输入，搭建同一独立 Device Service worker，下游隔离 Reviewer 只允许保存快照 dry-run。配置选择真实 `qemu` 来宾，并确认 worker 提供 `review-v1` 能力。
2. 通过独立测试代理转发标准保存快照审查，仅在第一个带 `review-v1` 的会话创建上设关口。在实际分配后扣住成功响应，或在转发前扣住原请求。通过 Reviewer 正常 `POST /api/reviews/{job_id}/retry` 启动，并读回持久创建记录的请求指纹。
3. 关闭自己拥有的 Reviewer 进程，重启同一数据库和相同 Device Service 连接配置。核对已创建关口的终态、未分配关口的协调结果，以及原请求晚到时的 409。已创建关口再用标准 Retry 测试不同的新会话和业务断言。
4. 在独立 ARM64 Linux VM 中用已固定的 STA SDK 固件和 Linux 原生运行时分别执行旧版、新版。标准 Retry 返回 202 后确认来宾及监督进程在同一独立网络命名空间内，读取活跃证据 ZIP 后重启 Reviewer。核对旧租约与进程，读取停止后的同会话 ZIP，最后标准 Retry 并确认恰好新建一个会话。
5. 停止前及停止后通过标准证据 API 核对同会话内容，结束自己拥有的其他租约，确保归零。发布记录保留哈希和有界结果，原始 ZIP、数据库路径、会话和进程标识仍保留在执行现场。

Firmware Burner 提交、浏览器测试与实体硬件测试均为 **NOT RUN**。
