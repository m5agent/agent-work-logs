# 固件审核的原生输入和虚拟 SD

2026-11-17，记录两条独立源码候选与 virtual-device validation。
StickS3、Cardputer、Cardputer-ADV、Core2 的指定输入已取到客体读回。Dial 控制器交付通过，原 UIFlow2 观察部分通过。K132、ADV、PaperS3 的虚拟 FAT32 实际挂载与读写通过。

- [报告与复现](report.md)
- [执行契约](run.json)
- [原生输入摘要](evidence/virtual-input-summary.json)
- [原版审核回放](evidence/review-replay-summary.json)
- [SD 摘要](evidence/spi-sd-summary.json)

合并、部署、浏览器-WASM 和物理验收为 NOT RUN。

[Dial 显式速度与默认反例](followups/2026-11-17-dial-physical-pacing/)补充实际边沿、原驱动计数及旧后端的拒绝回执。

[存储复用和同会话配网步骤](followups/2026-11-17-storage-and-staged-setup/)补充停止后导出、内部文件系统复位读回及原版配网关卡。

[PaperDIY、Cardputer STA 与 Tab5 上游候选](followups/2026-11-17-paperdiy-sta-and-tab5/)追加 SD 检测与复位、两板原生网络及 Tab5 DSI 对照。

[常驻切换与原版复审](followups/2026-11-17-resident-cutover/)记录发布后真实 HTTP 复测、数据面与历史留存。
