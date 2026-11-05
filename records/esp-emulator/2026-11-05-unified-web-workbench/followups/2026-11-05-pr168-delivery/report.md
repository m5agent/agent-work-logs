# PR #168 交付与生产验收

## 已完成的源码验证

复用首次记录的精确 `e31c2b4aed07c98fddea19018589f0f8751667c2`：
原生 CoreS3+PIR13项与静态导出 CoreS3 browser-WASM63项、最终 Python1973项（1963通过/10跳过）、
Node30、四生成器与分支范围检查已分别绑定。这里没有把 host 或 native 结果改写成线上 PASS。

## PR 与 CI

[PR #168](https://github.com/m5agent/m5stack-esp-emulator/pull/168) head 为 `e31c2b4aed07c98fddea19018589f0f8751667c2`。
[push CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41953432070) 终态 SUCCESS，
`network-namespace-policy` 和 `platform-contracts` 两个 job 均 SUCCESS。
PR触发的[独立CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41954037387)已双job SUCCESS。
PR于2026-11-05T02:19:47Z合并为 `082fffafd124800564d11c82b56cc4ecbb2c503d`，
head与merge的tree均为 `a9bd746d78ac2a31a560a4b4436e63f126504aae`，代码字节不变。
[merge main CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41954477899)也为SUCCESS。

## 发行包回读

准备包先上传至草稿发行附件并全量回读，随后发布为
[pages-unified-workbench-20261105-e31c2b4a](https://github.com/m5agent/m5stack-esp-emulator/releases/tag/pages-unified-workbench-20261105-e31c2b4a)：147,130,306字节，
SHA256 `73f87c9bbdc09d1d885df1bf2f538cca3cfa8da078c5d086124deb96e5c80353`，与本地已验包一致。
已验 manifest 为 `23e3fc8515b0f02b585bce0eb36e4e9f6579113d03ba96c6aafc12680f61844c`，
2,134资产、251,977,755字节，闭集与内容哈希已验证。附件回读证明包完整性；实际部署和在线执行分别核验。

## 清理

专用验证服务经核对没有活动会话和 lease 后关闭；native/browser guest 与测试浏览器均已清理。
仅停止拥有的验证资源，未操作用户服务。本段不公开私人环境地址或唯一运行标识。

## Pages与静态回读

[Pages workflow](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41954578004)的prepare/deploy均SUCCESS，
来源为main合并提交082fffaf；[生产站点](https://m5agent.github.io/m5stack-esp-emulator/)回读2,134资产、251,977,755字节，
87.722秒内逐项大小/SHA均与manifest一致，mismatches为空。静态回读不取代下一节guest结果。

本机原主目录从b41精确快进到082，保持clean，源JS/adapter/Unit assembly/HTML摘要与已验副本一致；
没有重启用户服务。

## 最终交付结果

| 项目 | 状态 | 依据 |
| --- | --- | --- |
| PR CI | PASS | 同head四个push/PR job终态SUCCESS |
| 合并 | PASS | 082fffaf与head同tree |
| Pages | PASS | 41954578004 prepare/deploy SUCCESS |
| HTTPS回读 | PASS | 同MF23e3，2134资产全量匹配 |
| HTTPS guest | PASS | 同站点完整63项及精确两阶段清场绑定 |

本轮交付链已实际完成。线上独立用例在UTC02:22:52.311至02:23:46.690执行，63/63检查、12次raw-paste及2次未修改默认程序通过，
manifest `23e3fc8515b0f02b585bce0eb36e4e9f6579113d03ba96c6aafc12680f61844c`，runtime manifest `fa6b56048ec91d100cb4f2a15088ce77e313bd2e6e8ba083229826b258297c51`，
WASM `96ea9f91956aa80926182ed174ea426f3f4c84e96ca58754fa249063fdda5ca1`，Flash `52f38f562f6e3749357a2ed4834efd72d16870046ea052f2f31691743cb5384d`。
独立HTTPS transport adapter只改变远程传输与身份核对，派生脚本 `5220fe8507157e9d547a76334c07ac768fcf7491d3f090675d38f82fd06c8b04`，
identity `dd8d714ec5feb1fdeb5ed613b3427a11010f617dcc7e0d43bbf0531dca4fdb89`；原完整功能断言保留。
原报告5,172,293字节/SHA `aa42c6ffb25499c3548423f7403d3daa5b6874694133c8958d018390759a8ed3`，不随记录复制大raw。
这些证据来自实际线上运行；CoreS3单例不能继承完整设备矩阵、其它Unit或旧运行时根因闭合。

实际线上清场与本地static用例不同：iframe移除前观察6个targets、live1且仅允许engine；
移除iframe后、context关闭前观察6个targets、live0。正常QMP退出0，5个pthread在退出时为0，forced/fallback均0。
不能描述为iframe移除前全部已关闭。临时验证依赖链接已移除，主目录与功能源码树均clean，所有拥有的guest/浏览器和临时服务均已清理。
