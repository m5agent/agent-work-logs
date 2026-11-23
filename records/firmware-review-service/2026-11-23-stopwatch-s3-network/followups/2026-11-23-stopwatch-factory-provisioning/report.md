# 技术报告

## 目标与实际行为

本条接续此前只到配置热点、或使用预置 NVS 的 StopWatch 网络验证，检查相同原版能否从出厂空配置完成自己的门户流程，并验证独立抓包摘要的重复报文边界。新出厂流程在 macOS arm64 隔离原生路径通过；Linux 和常驻部署不在本条验收范围。

原版 BIN 为 `606aac7831cb4ca2bd45fdac40f0755fc918d1c7772caeaafa7965ef72c64bac`，4,200,368 字节；归一化 16 MiB Flash 为 `f735f999d2fe6217f129fcc974edd08b0c5f9c8dca960dbadaa7b8669cf4474b`。原应用保持不变，NVS 初始全擦除，没有施加配置种子。最新原版执行使用 `e32e84ff933ab068be635c7aacd3ef1bae731c62` 的代码；`1e844f230d1ddaa1cc642cbf5b7bd0c2f65d4c26` 补齐 API inventory 和精确回放证据。它们目前是本地封存的源码身份，本文不声称已经发布到项目 main。

## 固定门户与控制器路径

原版的同步 JSON `POST /submit` 先测试 STA 关联，随后断开并保存配置；它本身不等于最后的 STA DHCP。读取 `/done.html`、再 `POST /exit` 后，原来宾才关闭配置热点并启动 station manager。新 profile 因此保留关联测试期间的 AP TCP 通道，并分别维护 AP 与 STA 状态。

执行使用默认关闭的 `stopwatch-open-softap-provisioning`。179 层原生序列中的补丁 0233 经正常控制器 TX/RX DMA 与 Ethernet framing 收发；固定 peer 通过同一 Unix socketpair 完成原门户及 STA DHCP/ARP，宿主 IP 后端为零。原生二进制 SHA-256 为 `5b8b3f24b9d2c757a21b1d17d635218348167d258b3e3677b69c3196cdf5d4db`，S3 ROM 为 `b5c7090cc22efce51c1323cef31ca96fcd673a5b1d1b1017e219d393f2659913`。这证明该虚拟设备路径的功能，不证明 RF、电气或任意网络安全隔离性质。

## 最新精确提交重放

实际发送六个输入请求：A+B 组合键、选择设置卡、打开设置、拖动到 Wi-Fi、点击原版 Wi-Fi 标签、开启 Wi-Fi。最新执行先匹配画面中的 Wi-Fi 标签再普通点击，避免固定滚动坐标偏移；输入、区域模板与帧 SHA 在摘要的 `exact_committed_replay` 内。

观察顺序为 AP 客户端 DHCP、门户首页、同步 submit、关联测试和保存、完成页、exit 响应、STA DHCP 与 ARP。只读 Flash snapshot 核对来宾写入的配置项及 CRC；同会话原生复位后，没有再次提交门户，仍得到新的 STA DHCP 和 ARP。

最新累计抓包 `8cce394e09139d8aac7760c19b4a67dd35a0212034d36c92a96e2022984393f7` 记录 3 次 DORA、2 个地址、4 条双向 TCP payload 流、0 条双向 UDP payload 流。复位阶段以独立捕获偏移核对新交换，不借用复位前证据。来宾写入 NVS 的 SHA-256 为 `b2255ce615cf13f14121e66a83fcf4d6894187f23a7f6b5f50f4a31f70bbe83e`；停止前 ZIP 为 `2274447d1c2c5c95224e8f04a94bf0efec0c098e2b5390d925055db714a74ef2`。ZIP 已在停止前保存，Flash 仅为 NVS 取证保留；peer、来宾和本例服务均已退出，租约归零。

## 独立 PCAP 摘要修复

`be59793ea2192d817bf45044bb538e01b7a933ec` 只修改摘要器、回归测试及生成快照。旧摘要的每事务序列上限为 32；真实 A1 中 67 次连续 DISCOVER 占满该数组，虽然后续 OFFER、REQUEST、ACK 仍在抓包里，下游无法识别完整顺序，也未把地址与双向流关联。

修复仅折叠连续同类型状态，所有原始包数、类型计数、选择/续租计数保持不变。32 个不同状态变化的上限仍在；真正超出时明确标记交易证据截断，由既有消费者维持 unknown。单 ACK、乱序、NAK、DECLINE、续租及截断负例均保留，未补造缺少的阶段。

同一 A1 抓包 SHA-256 `7a1a39ea1519128ec59df9f8c993870fe8d301391722e66ae160bd684acf6d72`，109,684 字节、358 包；其中 DHCP 71 包为 DISCOVER 67、OFFER 1、REQUEST 2、ACK 1。回放前后仅状态序列改变，其他完整摘要字段逐项相同；下游计数由 DORA `0`/双向 TCP `0` 修正为 `1`/`2`。这是历史抓包摘要修复，没有改变固件或控制器，也没有重新运行来宾。A1 当时只对 submit 后的关联测试作了过强预期，缺少完成页/exit；它的应用结论仍是 `PARTIAL`。

## 验证与保留的失败

出厂配网切面 `1e844f23…`：完整平台 2522 项、跳过 11 项、0 failure/error，202.684 秒；43 项针对性检查、9 项收尾检查、API pin 核对、源序列及新补丁正反恢复和四校验器通过。此前全量的一项 API inventory 摘要漂移失败保留，修复未改变操作计划。

PCAP 切面 `be59793e…`：28 项相关检查、独立完整平台 2522 项、跳过 11 项，229.454 秒；四校验器及 scope/diff 检查通过。相同合成重传用例在旧解析器上确定失败，在修复后通过；首次缺少 CI 依赖的执行保留为环境问题。两个全量结果来自独立源码切面，不能合并称作一份联合 release 验证。

首次固定行坐标点击误入 Button/Volume、未开启网络，保持为独立 `PARTIAL`。最终精确重放以可见 Wi-Fi 标签定位点击。旧 StickS3 门户的新 runtime 对照在 HTTP 阶段未完成，178 层基线在 submit 阶段也未完成；两者均为 `PARTIAL`，不能定位为 0233 引入的回归，也不能授予旧门户完整验收。

## 复现、范围与回退

在所记源码切面，用仓库 `scripts/bootstrap-unit-runtime.py` 重放固定上游 `40edccac415693c5130f91c01d84176ae6008566` 及补丁序列。原版应用功能经独立 Device Service 会话执行，按摘要中的实际六输入与门户顺序取证；原始 BIN、Flash、抓包、帧系列与敏感配置留在私有证据层，不随记录发布。独立解析器回归可运行 `PYTHONPATH=platform/tools:platform/tests python -m unittest test_pcap_summary test_device_service_wifi_evidence`，使用记录中固定的 CI 依赖。

本条新出厂 profile 和 PCAP 后续均未部署到 Linux/常驻；此前已配网 STA 常驻结果仍按前一条记录独立成立。未验证浏览器、物理硬件、WPA2、外部 Internet、云服务、任意门户及通用 HTTP 语义，未提交 Burner。回退为保持新 profile 关闭、保留此前固定 runtime 与生产解析器；本条没有执行生产切换。
