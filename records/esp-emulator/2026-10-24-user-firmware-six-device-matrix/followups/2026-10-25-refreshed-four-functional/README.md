# ESP Emulator refreshed four-firmware Device Service run

- 日期：`2026-10-25`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：公开 CDN 已刷新的 AtomS3R/PaperMono 四固件此前只有静态和 Manifest 证据
- 源码版本：`m5agent/m5stack-esp-emulator @ 259533cef424ffa0418369e2767a38862dc1b7d4`
- 基线版本：`fa66e1849756346946f3a6acf88757ac55d2c525`
- 环境：macOS Apple Silicon、Device Service `/api/v1`、QEMU、无物理硬件

## 结论

四个当前公开 BIN 已通过 Device Service 执行，并绑定实际 source SHA、
normalized artifact SHA、session、frame、input 和 serial digest：

- XiaoZhi Voice Assistant For AtomS3R：`PASS`，显示配网 UI；
- OpenAI Voice Assistant For AtomS3R：`PARTIAL`，NVS user data 缺失后
  `app_main()` 返回，稳定黑屏；
- EDC Book：`PASS`，显示启动/续读界面；
- CrossPoint-PaperMono-CJK：`PARTIAL/runtime_fixture_gap`，没有初始化 SD
  media fixture，显示 `SD card error`。

汇总为 `2 PASS / 2 PARTIAL / 0 FAIL`。Matrix PASS 只覆盖 frame/input/runtime
层，不等于语音、音频、文件读取或云服务完整功能。

代码侧新增 `runtime_fixture_gap` 分类和一个回归测试，避免错误页被 generic
“非黑帧 + 输入变化”规则误判成功能 PASS。

## 关键证据

- 平台测试：`357/357 PASS`；
- user firmware matrix：`17/17 PASS`；
- 文档契约：`19/19 PASS`；
- Node：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall 与 JSON 校验全部 `PASS`；
- CI：run `40126416761`，两个 job 均 `PASS`；
- 四个 Device Service session 均停止并保留历史，QEMU 已回收。

源码 evidence：
[refreshed four functional](https://github.com/m5agent/m5stack-esp-emulator/blob/259533cef424ffa0418369e2767a38862dc1b7d4/tests/firmware/evidence-2026-10-25-refreshed-four-functional/evidence.json)

## 文件

- `report.md`：执行、分类、证据和边界。
- `run.json`：结构化结果。
- `evidence/verification-summary.json`：脱敏验证摘要。
- `patches/`、`code/`：不适用；四张最终帧和 JSON 已提交到源码仓库。

## 未覆盖项

- CrossPoint 的 initialized FAT/SD fixture；
- OpenAI Voice Assistant 首次启动所需 NVS 数据与固件缺陷的区分；
- XiaoZhi 的语音、音频、配网完成和云连接；
- EDC Book 的外部书籍读取和长期导航；
- 完整 7 台设备及更多固件族回归；
- 物理硬件验证。
