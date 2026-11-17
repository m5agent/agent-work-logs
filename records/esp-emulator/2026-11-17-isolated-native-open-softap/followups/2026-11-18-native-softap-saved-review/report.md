# 隔离原生 SoftAP 的保存审核

## 固定夹具能力与审核

Device Service 1.82.0为 Cardputer、Cardputer ADV 和 StickS3 暴露板型固定的原生开放 SoftAP 夹具。仅当当前 QEMU 提供所需的 NIC QOM 布尔属性时声明能力。Cardputer 系列和 StickS3 使用各自固定 profile。Reviewer 通过显式 `native_softap_fixture` 启用，提前执行启动网络所需的已声明输入，再核对同固件同会话的停机后网络证据和 ZIP。夹具使用 Unix socketpair，无宿主 IP 后端。关联、ARP、DHCP、固定 HTTP 请求与响应、捕获终态及服务释放分别作为判据。

实测新 QEMU 的三个板型回报固定 profile，两个 Cardputer 共用 `cardputer-open-softap-fixture`。独立的旧 QEMU 仍可提供后端，三个板型均不声明这项夹具。该 HTTP 能力发现对照没有创建来宾。

同一 StickS3 无画面测试固件先等待 GPIO11。按住 BtnA 350 ms 后，来宾实际读到 GPIO11 拉低并输出启动夹具标记。最终捕获 24 包、一次 DORA、对应 ARP 和 HTTP 200，固定响应为 13 字节。按住等时的 BtnB 时，输入被接收，来宾实际读到 GPIO12 拉低并记录忽略。之后的检查点超时，终态只有一个捕获包，缺少 DHCP ACK 和 HTTP 响应，固定 SoftAP 取证为 `PARTIAL / pre_network_setup_incomplete`。

Cardputer 与 Cardputer ADV 分别以相同合并试验固件和各自的机器创建会话。两条均得到 23 个数据包、一次 DORA、匹配的 ARP 和同一固定 HTTP 正文。ADV 首次辅助审计错误地预期专属 profile，终态实际使用共享 Cardputer profile，已按实际 profile 核对 ZIP。两项本地网络均为 `PASS`。三个正向无画面夹具的整单审核维持 `manual_review / SIM_PARTIAL` 与 `E_NO_FRAME`。活动租约为零，Flash 均已释放。 [三个固定夹具、按钮负向与能力对照](evidence/native-fixed-softap-saved-review-summary.redacted.json)

## StickS3 Assistant 原版门户对照

原版 Assistant 的同一保存快照在 `9d27879b55bcc6abc2c0e77163853867f19f1a6b` 和原生 QEMU `7e63fc223c6946ef8b2f44b1510d904aea6cc7c36c21324bb631490a3f325b24` 上从门户提交走到本地 STA。最终捕获 116 个数据包，完成两次 DORA，两份租约有对应 ARP 回复。门户页面和提交响应均为 HTTP 200，原报告的本地判据为 `PASS`。实际证据 ZIP 的预停止捕获是最终捕获的字节前缀，标准化 Flash 摘要与 ZIP 会话清单相符。整件审核保留 `manual_review / SIM_PARTIAL` 和 `E_NETWORK_PARTIAL`。云端功能为 `NOT RUN`。隔离进程退出，活动租约为零。 [原版门户到 STA 基线](evidence/sticks3-original-provisioning-summary.redacted.json)

保持原版和标准化 Flash 摘要、运行时不变，用 Device Service `01073526950164493f749f6908ba5ee0d224c0a0` 和 Reviewer `ef813f5a9e40ccacf1dd5d4945cbedcc87b0933d` 重放。最终捕获 114 个数据包，两次 DORA 及对应 ARP，两个 HTTP 200 的响应正文分别与基线逐字节相符。ZIP 所带抓包与最终抓包逐字节相同，清单的 Flash 摘要与基线相符。来宾引导与本地门户为 `PASS`，整单仍为 `E_NETWORK_PARTIAL`。这两次原版回放与四个固定夹具会话均已停止，隔离服务均已退出。 [原版基线与重放](evidence/sticks3-original-provisioning-summary.redacted.json)

模拟器主分支为 `9bbbcba8477039c8e35cf85b002c6b63a83cae86`，包含已执行的 Device Service 产品变更与对应数据摘要。平台本地测试 2,417 项，跳过 10 项，零失败。Reviewer 主分支本地测试 214 项通过。文档 51 项、差异范围和四个生成校验通过。远程 CI 在归档时仍在进行。 [对应源码和有界记录](https://github.com/m5agent/m5stack-esp-emulator/blob/9bbbcba8477039c8e35cf85b002c6b63a83cae86/tests/network/native_open_softap/saved-review-summary.json)

实机、浏览器、常驻部署与 Burner 提交为 `NOT RUN`。
