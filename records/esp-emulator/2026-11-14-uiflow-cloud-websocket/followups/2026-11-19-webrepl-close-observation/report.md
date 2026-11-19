# CoreS3 原版 WebREPL 断开观测复验

## 背景与改动

此前同一 CoreS3 原版的两类接收错误有不同的包级证据。未绑定身份收到云端错误后由对端先发 FIN。授权身份完成文本心跳，控制 Pong 缺失，设备报告 120 秒超时再先发 FIN。旧会话快照能看到相关计数，但缺少断开方，文字与控制帧的往返也没有独立字段。

Device Service 1.99.4 新增 **text_heartbeat_roundtrips**、**protocol_ping_roundtrips** 和 **last_disconnect**，保留旧字段以及原先最近连接的计数范围。最近连接尚在运行时仍可报告先前最近一次已确认的断开。关闭方来自抓包中观察到的第一个关闭信号，包括 WebSocket Close、TCP FIN 与 TCP RST。新信息供诊断使用，工作台和服务自身的就绪条件沿用原有语义。[固定源码与契约](https://github.com/m5agent/m5stack-esp-emulator/commit/a1066b0d4da60e28c63addaf93103f6713e3f8c4)

## 执行环境与步骤

| 层 | 固定证明 |
| --- | --- |
| 原版 CoreS3 BIN | 5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded |
| 规范化 Flash | 480ca4a24c1c1b56deef1218f8533bf5b00c9e33a98f3b3f705e2569b53051c0 |
| 历史抓包使用的 Xtensa 运行时 | 5ce7d9f5ce397ce87935626c0284955714e0ed286fcce0cd91ca47f4f326040c |
| 基线 Device Service 1.99.3 | 2a7f979c0c7e67420d8b790a3cfdb692702abf05 |
| 候选 Device Service 1.99.4 | a1066b0d4da60e28c63addaf93103f6713e3f8c4 |
| 候选运行时 OpenAPI 字节 | de40f9f908869b7eb1cf9a775887acd209c75644bf44277d098659fc8defd914 |
| 浏览器 | Chrome 157.0.8103.79 |

1. 对照历史 ZIP 和清单内抓包的长度与 SHA-256，将三份数据装载到独立服务的停止会话。保持原抓包字节，重放状态只包含复验字段。
2. 使用正常的 GET /api/v1/sessions 和会话详情读取状态，验证两者的 WebREPL 字段一致，并逐字节读回该版本的 OpenAPI。
3. 打开两版实际的会话历史界面并检查三张历史状态卡。记录分层心跳和断开信息是否可见，统计页面错误和非只读请求。
4. 确认零租约、零新来宾后退出隔离服务并移除回放的临时副本。输入 ZIP 与 PCAP 摘要及页面状态卡片指纹见[基线](evidence/baseline-replay-summary.json)与[候选](evidence/candidate-replay-summary.json)。

## 结果

| 原版历史抓包 | 配对码回执观测 | 有效握手 / 断开 | 最近连接文字 / 控制往返 | 最近断开 |
| --- | --- | --- | --- | --- |
| 未绑定 | 有 | 20 / 20 | 0 / 0 | 对端先发 TCP FIN，之前 0 个未回应控制 Ping |
| 授权后超时 | 有 | 1 / 1 | 5 / 0 | 设备先发 TCP FIN，之前 4 个未回应控制 Ping |
| 授权后重连 | 有 | 2 / 1 | 1 / 0 | 仍保留上一次设备先发 TCP FIN，之前 4 个未回应控制 Ping |

第三份抓包中开放的新连接已发出两个控制 Ping。历史全抓包统计共有七次文字往返，API 按最近连接返回一次，断开条目对应前一个连接。基线与候选的原有最近连接计数一致。页面中的配对状态仍提示收码和账号绑定的区别。两个浏览器回放均无页面错误、非只读请求及外部网页请求。

独立无设备身份的公网宿主探测收到有效 HTTP 101、一个分类为应用错误的文本帧和 TCP EOF，未观察到 WebSocket Close。该探测未发送控制 Ping、应用命令或设备身份，结论限于匿名入口。授权路径还需使用云端所有者批准的测试身份复验。[匿名宿主摘要](evidence/anonymous-upgrade-summary.json)

候选全量 Python 平台测试运行 2515 项，10 项跳过。完整 Node 合同测试通过。真实抓包验证覆盖 TCP FIN 和重连展示，其他关闭信号通过定向合同覆盖。[WebREPL 定向 Python 合同](https://github.com/m5agent/m5stack-esp-emulator/blob/a1066b0d4da60e28c63addaf93103f6713e3f8c4/platform/tests/test_uiflow_cloud_status.py) · [浏览器合同](https://github.com/m5agent/m5stack-esp-emulator/blob/a1066b0d4da60e28c63addaf93103f6713e3f8c4/platform/tests/test_uiflow_cloud_status.mjs)

## 边界与回退

本条记录支持原版留存抓包在候选 API 与界面中的诊断准确性。授权云端持续连接仍待跨多个超时周期复验，远程代码执行、物理硬件、实际云服务修改和常驻部署均未在此次验证范围执行。Burner 未提交。回退到基线可恢复旧快照与显示字段，原历史证据继续可读。

公开文件只保留无身份计数、状态、版本、回放检查与 SHA-256。原始抓包、原 BIN、完整会话标识、配对码、截图和执行端点均从公开材料省去。
