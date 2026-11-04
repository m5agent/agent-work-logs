# ESP Emulator UIFlow browser workbench：限定验收记录

- 日期：2026-11-04
- 结果：PARTIAL（工程功能与host验证PASS；模型根因及性能边界保留，PR已合并，正式发布尚未完成）。
- 工作类型：code_change、report。
- 来源：用户要求全部19款已准入浏览器设备提供默认UIFlow代码工作台，并核验启动、输入、编辑器及限定性能；无公开Issue编号。
- 源码：[公开提交](https://github.com/m5agent/m5stack-esp-emulator/commit/c3db057d2ee99c022a4116ae72d661c4d39888c6)，base b41eba70eb61f7ddc5c41e0b981341064f9d1d1f；源码推送与commit回读已通过。
- 环境：QEMU/WASM75、Emscripten3.1.50、实际Chromium/ANGLE；browser-WASM virtual-device validation，未操作物理设备。

## 结论

19款默认镜像及真实UART MicroPython工作台已实现。V6/e597上的R8完成60/60例：
19editor、19普通按键、Cardputer56键公开IRQ、StackChan三区body-touch、20fixed，
共2,564项检查、224次raw-paste、38次未修改默认源码Run和200个输入subject-trial。
父报告35,220字节/SHA4265d32ff912502cb000d6795f1fbd52bcb3795fc54ccb3f83d522db863a343a，
UTC06:54:09.317至07:20:47.704；逐项独立复核全部60原报告byte/SHA及exit0。
[严格60例摘要](evidence/all19-acceptance-summary.json)与源码原文件逐字相同，
63,855字节/SHA9703b94a23025b75be4c8464e32ac835cc75fffa10f5fcc9d88bc144de841151。

最终c3db源码的host R2九步骤全PASS：Python1967项=1957PASS/10skip/0fail，
Node28/noSKIP、collector9、四validators及diff/scope通过。首轮3项文档FAIL与定点21PASS
保留。10skip准确包括2个optional littlefs测试运行时、1个pinned compiler、7个pinned
UIFlow source checkout；littlefs-python0.19.0已安装，不能写成依赖包缺失。
[host证据](evidence/final-host-summary.json)含逐步骤命令、日志byte/SHA和最终49文件绑定。

四组独占槽cold-prime→same-page warm方法均完成，8phase/164原检查通过：
75 Matrix53.491→76.480s、75 Plus39.378→63.627s、
3c Matrix109.448→108.710s、3c Plus96.703→111.456s。
结果混合，75两组更慢；公开CoreS3→target模型重建使其不能证明纯cache或严格仅rerun收益。
首次3cMatrix pre-Start observerFAIL及无效warm计时独立保留。此前独立cold-only
54.775s/39.144s不被这些新cold-prime值替换。

原FAIL不被后续PASS抹去，RUNTIME-07/08/09根因仍OPEN；精确11个S3 Flash/main策略
不能转授未知固件、共同C根因修复或长期稳定。PM1是显式500ms应用窗口与250ms输入；
Cardputer Fn pointer带grave键盘伴随。普通buttons/Card缺held-iframe外部CDP仍标
NOT CAPTURED。SDK pthread cancellation未建立，物理/线上性能均无新增证明。

## 关键证据与文件

- [report.md](report.md)：实现、失败时间线、复验与边界。
- [run.json](run.json)：结构化状态、最终源身份和文件引用。
- [主摘要](evidence/validation-summary.json)：包装、保留FAIL、来源和交付状态。
- [all19摘要](evidence/all19-acceptance-summary.json)：精确60例功能；max2并行，不作性能样本。
- [DOM摘要](evidence/dom-qa-summary.json)：V5局部model-only、guest NOT RUN，首observerFAIL保留。
- [readiness摘要](evidence/readiness-summary.json)：19板初次就绪观察，max2功能环境，不能作独占性能或跨板排名。
- [warm摘要](evidence/warm-summary.json)：四组原镜像、方法、缓存和双阶段清场，逐字保留源文件。
- [host摘要](evidence/final-host-summary.json)及[首轮FAIL](evidence/final-host-r1-failure-summary.json)：R1/定点修复/R2和普通远端CI。
- patches/、code/不另附；实现和复现入口随公开源码提交提供，不归档raw日志/帧数组/固件二进制。

## 交付范围

[普通源码CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41796558326)两个job完成SUCCESS；它不是regular Pages60guest job。
首次归档时PR尚未创建；交付后续见下节。main合并、Pages发布及在线同路径验收均NOT RUN，等待授权。
本记录分别保留实现、验证与尚未执行的交付状态。

## PR #165 交付后续

2026-11-04T08:24:25Z：PR已创建，精确head为c3db，push/PR两轮普通CI四检查均通过。
[交付与边界记录](followups/2026-11-04-pr165-handoff/report.md)保留实际回读及此前功能证据的复用范围。
合并、Pages和在线验收仍未执行；首次归档状态保留在原固定提交。

## 合并与首次正式发布尝试

PR #165已按授权合并为23d38d8d，文件树与原c3db验证版本一致，普通main CI通过。
[发布检查点](followups/2026-11-04-pr165-merge-publish-attempt1/report.md)固定首次下载TLS失败及其后一次同源码恢复尝试。
截至该检查点，尝试2仍在正式构建中，尚未授予新站点或线上验收通过。

## 后续发布资格失败

正式尝试2完成源码构建后，Matrix首例在600秒内未达到应用ready；同版本CfT本机单例通过不能转授托管结果。
新的main精确导出复验为16PASS、AtomS3 Lite复位1FAIL、43NOT RUN；现有公开站点尚未替换。
[独立失败与控制记录](followups/2026-11-04-pr165-release-qualification-failures/report.md)保留三条路径及各自身份、清场和未执行边界，原因仍待定位。
