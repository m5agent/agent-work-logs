# 官方文档反馈调用

Skill 发现可复现的资料错误、缺失、损坏示例或其他反馈时，按模型和版本整理出处、实际结果与期望。使用原版助手的 `knowledge_feedback`。没有原生工具时，随包的 `scripts/feedback.py` 走同一官方 MCP 方法，并标明 `source_tool=other`。收到肯定的 `accepted` 和非空 `feedback_id` 才确认提交。回执不明时先核对状态。

拆包运行 `python3 scripts/feedback.py --check`，真实服务完成握手和工具枚举。用隔离的 aarch64 Linux 来宾挂载同一 ZIP，在关闭外部网络的环境内运行模拟 MCP。检查 JSON、文本包裹 JSON 和 SSE 三种成功回执，以及缺少编号、明确拒收、RPC/HTTP 错误、缺少工具和非法类别等情况。验证副作用请求每次只发一次，发现流程和无效输入没有执行反馈调用。生产写入未执行。

发布后将远端下载包与本机包逐文件比对，共 4,390 个文件一致。本次 ZIP 基于上一版站点语料构建。
