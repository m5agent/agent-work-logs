# PR #170：Unit预览与本机Preview交付后续

- 日期：`2026-11-05`
- 结果：`PARTIAL`（本次限定交付完成；其它型号、Unit与物理性质未重测）。
- 来源：[PR #170](https://github.com/m5agent/m5stack-esp-emulator/pull/170)。
- 源码：head `22001fe1cb6bb44eb2737872e4cc578605e57921`，合并 `84b4f4932a402b77c9688aff7b51a1932ff12be6`，tree相同。
- 环境：源码CI、正式发行附件完整回读、Pages，以及授权的现有本机Python服务更新。

PR已合并，四项CI与合并后main CI成功，正式发行附件完整下载的大小与SHA相同；Pages部署成功，实际HTTPS manifest身份相同。
实际HTTPS全2134资产/251,980,691字节零mismatch；现有服务的HTML/JS/CSS逐字匹配合并源码。实际HTTPS CoreS3完整65项通过，含12程序、2次默认Run、预览保持打开与正常双阶段Worker清理；实际本机只读页面13项通过；没有在该服务创建guest。

- [report.md](report.md)：交付、保留失败与范围。
- [run.json](run.json)：结构化分层状态。
- [delivery-summary.json](evidence/delivery-summary.json)：已确认交付身份和分层边界。
- [线上CoreS3摘要](evidence/https-browser-summary.json)：MF23ee/WASM96ea/FW52f、原程序与reset、中断及6/live0双清理栅栏。
- [实际本机页面摘要](evidence/actual-local-host-ui-summary.json)：派生脱敏HTTP/UI观察13项，无API写入或guest。
- [首次记录](../../README.md)：host20、原生14、浏览器65与完整检查；历史失败均保留。

未给实际用户服务授予guest PASS；独立原生14项是相同产品认证路径的guest证明。其它型号、Unit、物理性质和性能不继承。
