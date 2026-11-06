# 公开安全派生证据

以下文件由白名单字段生成，不是 raw。删去了实际端点、机器路径、私有凭据、原始
会话/执行/worker/进程身份、串口 nonce、HTTP 路径与响应正文。每份稳定原始报告保留
SHA256 和字节数，使用语义别名关联 guest、固件、运行时、帧和清场结果。

- [run-1-summary.json](run-1-summary.json)：首次原生观测失败，未改写为通过。
- [run-2-summary.json](run-2-summary.json)：阶段检查、红绿帧、Relay 观察与后续独立启动失败。
- [run-3-summary.json](run-3-summary.json)：旧标签全文断言与 compact label 设计不匹配，保留 oracle 失败。
- [run-4-summary.json](run-4-summary.json)：完整 25 项原生通过；真实 guest 与逻辑压力夹具分开。
- [source-identity-summary.json](source-identity-summary.json)：每轮报告哈希回核及 run-4 八个源码工作树绑定；最终源码提交已绑定。
- [run-5-summary.json](run-5-summary.json)：自动巡展真实阶段 27 项通过，逻辑压力场景布局漂移失败；保留产品缺陷。
- [run-6-summary.json](run-6-summary.json)：最终自动无输入 31 项通过，逻辑压力存活位置稳定；原 run-5 失败保留。
- [final-automatic-followup-summary.json](final-automatic-followup-summary.json)：最终自动版 3.624473 秒短任务、401 GET、14 guest 清场与 15 源码哈希绑定。
- [restart-followup-summary.json](restart-followup-summary.json)：run-4 版本重启恢复、purged 内容不可读及零 guest 复活；寿命 3.905601 秒。
- [host-validation-summary.json](host-validation-summary.json)：前两次全套失败、修复、第三次 2,035 项通过及 Node 合同；覆盖自动巡展前版本。

自动巡展最终验收已通过；最终源码与生成器检查已完成，源码已推送，最终文档全 50 项复跑通过；归档由仓库脚本发布。截图只保留尺寸观察，未复制带身份信息的图片。
