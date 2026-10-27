# Evidence summary

本目录保存可公开的派生证据：

- `summary.json`：runtime、issue、firmware、session、frame、串口 marker 和
  data-plane 摘要；
- `frames/`：九个 Device Service 最终 PNG；均无 metadata，已检查为
  只含 RGB frame pixels。

未发布原始 evidence ZIP：每个 ZIP 的 Service manifest 含唯一 device code。
公开摘要保留 ZIP SHA256 和结论所需数据，删除了唯一设备标识、内部服务路径
以及与本问题无关的原始请求/响应。因此这些文件明确是 summary/derived
evidence，不应被标记为 raw。
