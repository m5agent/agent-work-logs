# 身份能力跟进复现

使用 Python 3.12+ 与固定源码 checkout。`summarize_private_evidence.py` 和 `summary.schema.json` 与前序已公开记录逐字一致；只离线读取受限大小的 ZIP/PCAP/serial，输出白名单计数、布尔、哈希和相对时间。原输入不得进入公开仓库。

执行复现时保持原 BIN、执行源码、运行时和板型一致：

1. 连接未广告身份能力的真实旧服务，分别请求 MAC 与持久 key。预期在创建 POST 前拒绝，不启动 guest。
2. 在支持能力的版本上打开真实浏览器入口，先完成连接。指定操作者获授权的身份，记录实际 POST 和响应；匹配身份后才允许显示运行。
3. 握手后观察至少 195 秒，区分收到配对码、云端登记、文本心跳、控制心跳和远程执行。保存全程网络事件，预先声明准备/运行/清理边界。
4. 留空另跑默认 key 分支，核实际请求和 persistent-fixture/key 收据，不用省略字段的旧运行代替。
5. 每次先取同会话 ZIP，再停止，核 Flash/lease/guest/浏览器退出且历史保留。不要覆盖失败。

下列变量由操作者设置，具体值不公开；观察器 checkout 必须与声明的模块哈希相符。

```sh
python3 code/summarize_private_evidence.py \
  --tools-dir "$CHECKOUT/platform/tools" \
  --zip "$PRIVATE_EVIDENCE/evidence.zip" \
  --case candidate-authorized \
  --source-commit 3a4408e4a1f26c0c8ad3ff07dae1ac8149a50384 \
  --observer-source-commit 3a4408e4a1f26c0c8ad3ff07dae1ac8149a50384 \
  --runtime-identity "$PRIVATE_EVIDENCE/runtime-identity.json" \
  --terminal-state "$PRIVATE_EVIDENCE/terminal-state.json" \
  --output evidence/new-authorized-redacted-summary.json
```

源码提交参数由操作者提供，不由 ZIP 自证；本跟进另以冻结源码清单、执行命令和真实文件哈希绑定。当前第三轮浏览器版本和执行文件哈希未在当时记录，故复现不主张浏览器版本完全相同。新的对照应在启动时记录这些值，不能追认旧运行。

最终主分支复验是另一轮执行，源码为
`70ef503fc2fb8b2c787fa9065e2952f525c40099`，其浏览器版本与二进制SHA在前后均采集。
上面的 `candidate-authorized` 命令仅复现先前候选摘要，不将其输出重标为最终执行。
最终证据的独立协议复算使用固定源码中的观察器，具体模块SHA、PCAP和serial SHA见
`../evidence/final-main-cloud-protocol-summary.json`；受限原ZIP不能公开下载。
复测应重新执行同一浏览器/原BIN路径，并生成自己的同会话证据，不复用历史状态。
