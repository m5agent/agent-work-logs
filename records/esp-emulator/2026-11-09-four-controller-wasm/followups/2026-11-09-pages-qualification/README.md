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

## 后续资格试验

串行本机门禁在 StackChan 触摸用例的客体启动阶段出现内存映射断言。随后同镜像的独立重放通过 35 项触摸、I²C 和清理检查。两个结果分别保留。

引擎自关闭候选完成三次全站试验。首轮在 PaperMono 验收源码的换行转义处停止。修复后下一轮出现两款 Paper 的短输入漏读，真实 Worker 回收通过。等待两段实际约一秒心跳后，两款 Paper 的同样 250 毫秒诊断分别通过。第三轮全站在 StickC Plus2 的 CDP 引擎残留处停止，34 例通过、1 例失败、37 例未运行。独立候选没有获得发布资格。

修订下载路径后，最新[托管任务](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42585733928)从 `f806c2a7b220f8491d0e034a05fd5e57d72b48cb` 构建了两套运行时，原版 CoreMatrix 浏览器验收通过。全站及公开 HTTPS 验证分别记载。

- [串行 StackChan 启动失败](evidence/stackchan-serial-startup-failure-summary.json)
- [StackChan 同镜像复跑](evidence/stackchan-startup-replay-summary.json)
- [候选第二次完整试验](evidence/self-close-full-gate-summary.json)
- [两款 Paper 的短输入诊断](evidence/paper-input-cadence-summary.json)
- [候选第三次完整试验](evidence/self-close-final-gate-summary.json)

## 托管终态

两套源码构建与官方 CoreMatrix v2.5.4 原镜像验收完成。全站门禁完成三例，Atom Matrix 的编辑器和按键两例通过，StickC Plus 编辑器在真实 CDP 回收检查失败，余 69 例未运行。失败会话的固件编程及复位成功，QEMU 退出码为 0，五个内层 pthread 已关闭，仅一个独立引擎目标仍登记。部署步骤跳过。独立读取正式 HTTPS，仍为 19 款旧浏览器配置，四款新配置尚未上线。

[托管逐项证据与正式站点读回](evidence/hosted-full-gate-and-live-readback-summary.json)
