# Pages 发布资格与下载诊断

- 日期 2026-11-09
- 结果 `PARTIAL`，四款限定客体路径和源码 CI 已通过，完整 Pages 发布资格独立执行。
- 源码 [PR #198](https://github.com/m5agent/m5stack-esp-emulator/pull/198) 合并 `3c47006212a6ad08623e7bc34cba707b347be753`。
- 环境为 macOS Chromium、同一双 WASM 静态导出及 GitHub Actions。

发布用的本地导出加入 23 款正式浏览器配置，2,175 个资产逐个核对长度和 SHA-256。原版 CoreMatrix 在公开镜像校验下再次通过，实际 CDP Worker 全部回收。全站并发门禁在旧设备 AtomS3 Lite 的单个引擎 Worker 残留处停止。源代码改用主页面作为浏览器引擎的 Worker realm，两次单板按键及原版 CoreMatrix 通过，但第二次并发全站门禁仍在 AtomS3 Lite 的编辑器清理处复现。两个失败的后续用例保持 `NOT RUN`。

[托管发布运行](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42582197362) 的首次及第二次尝试均在 Xtensa 依赖下载阶段收到 HTTP 504。两个托管日志均已完成 C/QEMU 补丁重放及 Emscripten 版本检查，具体请求文件未打印。本机同下载代码复现 libffi 官方直链的 504，通过同一上游 GitHub Release API 成功读回。libffi、PCRE2 和 WrapDB 三份 API 下载均与两个目标锁文件的 SHA-256 完全一致。正式工作流调整仍需独立执行。

- [首次完整门禁失败](evidence/first-complete-gate-summary.json)
- [父页面引擎方案第二次完整门禁失败](evidence/second-complete-gate-summary.json)
- [公开配置下的 CoreMatrix 原镜像](evidence/corematrix-public-profile-stock-summary.json)
- [AtomS3 Lite 两次独立验收](evidence/atoms3-lite-parent-owner-summary.json)
- [AtomS3 Lite iframe 存活对照](evidence/atoms3-lite-iframe-diagnostic-summary.json)
- [PaperS3 iframe 存活对照](evidence/papers3-iframe-diagnostic-summary.json)
- [结构化记录](run.json)
