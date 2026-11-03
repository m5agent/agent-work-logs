# ESP Emulator 性能修复与分层验收

- 日期：`2026-11-03`
- 结果：`PARTIAL`。固定固件的性能与功能验收通过；StackChan 官方 Factory browser 故障仍未解决。
- 工作类型：`code_change`、`report`。
- 问题来源：用户要求解释并修复同设备、同固件相对于[参照模拟器](https://zhuzhe1983.github.io/esp-online-tester/platform/)的启动慢和运行卡顿。
- 源码版本：[m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)，base `3691870c27b028dde76202e42ecddba31d1547c1`；R6 被测 source `8dd39cac835f6325a3f0aa815ca0d8471b025e6b`；最终交付 source commit：`69b26f3b72e7a3246048d58f6b77d649155790a7`。
- 环境：Apple M4、实际 Metal 模型画布、独立静态 browser-WASM；native 使用独立 Device Service。各 lane 独立取证，无物理硬件测量。

## 结论

保持单一 QEMU TCI，没有并入第二 SoC 模型或实验 JIT。修复包括校验缓存和并行加载、final-link O3、typed helper、有界 GPIO 事务、精确固件绑定的正常时钟/单指令 TB、独立帧/输出轮询及 native SCS→DOM→3D 桥。

最终 R6 同一 `c854…4542` dance BIN 的应用 ready 为 cold **3.559 s**、同页 repeat **2.746 s**；20 秒内实际 packet 增量168/166、位置变化165/163。独立可信触摸为509.03 ms，真实 guest 响应在 down 后96.80 ms。R6 既有19板/20固定例、552/552检查通过。像素/回调更新不是完整应用帧或物理 FPS，已保留全部观测长间隔及启动静态画面/按需 render 的上下文。

CoreS3 原始参考程序 `789612…` 的 R5 composer ready 为13.151/11.876 s；R4 StopWatch 的首非黑为5.655/5.083 s，并有真实 A+B 与完整菜单 ROI 证据。这些轮次和来源不冒充 R6 的性能观测。官方 Factory 的真实 WDT/Double 失败、旧测试假阳性及早期 Cardputer 失败均保留。

## 关键证据

- 构建或运行：[fresh72 source build](evidence/build-r4-summary.json)、[R6 dance/touch](evidence/browser-final-stackchan-summary.json)、[独立重算](evidence/stackchan-final-independent-summary.json)。
- 产物或部署：WASM `0bd9478743d640484cad4762b9d7f7ae57a222f83ebf12a2114eb764a05194ea`；[最终固定例门禁](evidence/admitted-browser-summary.json)。未部署，未声明 merge。
- 实机或服务执行：物理实机不适用；保留 [native r4 execution](evidence/native-summary.json) 与 [R6 有限源码等价证明](evidence/native-final-path-summary.json)，后者不是新 native guest。
- 日志、测量或协议：[启动间隔上下文](evidence/startup-gap-summary.json)、[原版 CoreS3 R5](evidence/browser-stock-compose-summary.json)、[R4 StopWatch/历史产品路径](evidence/browser-r4-summary.json)、[oracle 修正](evidence/oracle-correction-summary.json)、[方向重绘](evidence/orientation-repaint-summary.json)。

## 文件

- [report.md](report.md)：根因、实现、测量、复现和边界。
- [run.json](run.json)：原 native execution 保持不变，follow-up execution 分轮追加。
- [evidence/manifest.summary.json](evidence/manifest.summary.json)：脱敏派生证据的 SHA/大小；这些文件不称 raw。
- [完整源代码修复补丁](patches/0001-qemu-performance-repair.patch)：对公开 base 可直接应用，独立 checkout 应用后的 Git tree 与最终提交完全相同；使用 `--unidiff-zero`。
- `code/`：不另复制；实现与测试代码包含在上述完整补丁中，命令见 report。

## 未覆盖项

Factory vendor browser 仍 FAIL；完整物理时序、电气/RF/声学/机械、任意固件、长稳与其他主机未验证。Python 3.12.14: 1942 tests, 10 skips, all remaining passed; Node contracts and required generated/source/diff checks passed. 本记录交付可审查代码与复现证据；未合并或部署生产网页。

[最终代码检查](evidence/host-production-checks-summary.json)与[补丁应用验证](evidence/patch-apply-summary.json)分别记录，不替代固件实测。
