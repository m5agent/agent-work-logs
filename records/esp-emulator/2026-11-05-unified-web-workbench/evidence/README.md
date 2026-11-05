# Evidence summaries

此目录只保存经过筛选的派生摘要，所有文件均非 raw evidence。
私人端点、宿主路径、认证值、会话标识、设备唯一标识、浏览器目标标识和 nonce 均不进入本记录。

- [implementation-review-summary.json](implementation-review-summary.json)：源码观察、根因与接口边界。
- [host-contract-summary.json](host-contract-summary.json)：已完成的限定 host 控制；最终汇总待补。
- [workbench-host-copy-final-summary.json](workbench-host-copy-final-summary.json)：最终前端副本 Chrome host18。
- [workbench-host-summary.json](workbench-host-summary.json)：上一轮 Chrome host18、四次 observer FAIL 和中间17项 PASS。
- [native-summary.json](native-summary.json)：精确 native CoreS3+PIR 13项与全部先前失败。
- [browser-summary.json](browser-summary.json)：完整 CoreS3 browser-WASM 63项与正常清理。
- [final-source-validation-summary.json](final-source-validation-summary.json)：最终完整检查与两轮元数据失败。
- [prepared-archive-summary.json](prepared-archive-summary.json)：最终可重建静态包闭集，仅包装完整性。
- [validation-summary.json](validation-summary.json)：保留的前提/observer 失败及尚未绑定的 guest 结果。

原报告以 SHA256 和字节数保留可核对身份；摘要不暗示读者能够从本仓库取得未公开的原始日志。
