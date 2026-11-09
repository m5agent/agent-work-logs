# #178 与 #190–#193 修复及验证

整合源码 `42bb6b53dae18265a0e64c4c6775d87c564a07e7` 基于 `dd2eb35d2e6a909992268089ddc37e27970d4a92`。三份原生运行摘要均记录 QEMU SHA256 `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`。各次固件、输入、串口、帧、协议与清理按实际路径记录。

## #190 设备档案

| 字段 | 原值 | 修正值 | 官方依据 |
| --- | --- | --- | --- |
| NanoC6 SKU | `C122` | `C125` | [产品页](https://docs.m5stack.com/en/core/NanoC6) |
| Dial 机身尺寸 | `45 × 45 × 32.3 mm` | `51.0 × 51.0 × 32.3 mm` | [产品规格](https://docs.m5stack.com/en/core/Dial) |
| AtomS3R-CAM 机身尺寸 | `24.0 × 24.0 × 14.0 mm` | `24.0 × 24.0 × 13.5 mm` | [描述和产品规格](https://docs.m5stack.com/en/core/AtomS3R-CAM) |

从设备目录源修改三项值，再同步相关的派生目录、单设备 JSON 和 README。元数据摘要逐项校验可用字段。尺寸来自公开产品规格，物理测量属于 `NOT RUN`。

## #191 Unit 研究记录

Joystick2 改为 `U024-V2`，ENV-Pro 为 `U169`。原 ENV 记录仍包含现存精度说明差异。[Joystick2](https://docs.m5stack.com/en/unit/Unit_Joystick2) · [ENV-Pro](https://docs.m5stack.com/en/unit/Unit_ENV-Pro)

TimerPWR、Step16、DoF6 和 CardKB2 均有公开 UIFlow2 驱动及文档。逐一下载记录中的固定公开版本，共八份文件，SHA256 与目录证据相同。旧 raw-I2C 或通用 BMI270 观测仍按原探针范围描述。runtime profile 对比只有五个 `blocker` 字符串有变化，覆盖层级、主机和绑定等其它字段通过等价比较。[驱动与文档摘要](evidence/catalog-summary.json)

ADC v1.1 使用 ADS1110 和内部 2.048 V 参考，采样率为 15、30、60、240 SPS。原 ADC 的 ADS1100 使用 VDD 参考，采样率为 8、16、32、128 SPS。官方比较表已区分两列，目录清理了旧文档矛盾提示。[ADC v1.1 产品页](https://docs.m5stack.com/en/unit/Unit_ADC_v1.1)

## #192 基线帧采样

已报告的负载下故障发生在输入前固定等待后的截帧。StackChan 的 guest 串口已经出现就绪与外设数据，但前帧仍全黑，延长观测后可得到正常基线。Core2 AXP192 也曾出现同类瞬时失败。[故障描述](https://github.com/m5agent/m5stack-esp-emulator/issues/192)

`run_profile_ui_test.py` 接受非负有限的 `--before-frame-timeout`。默认仍单次抓取。StackChan 外设和 Core2 AXP192 在原 settle 后最多以 10 秒采样期限等待既有非黑像素和颜色阈值。采样之间等待至多 100 ms。尺寸、进程退出和超时保持错误路径。最终方案用 StackChan 已有的初始化完成标记约束同序 QOM 写入，在 Core2 回归探针新增 ready 与 draw-complete 标记。输入坐标、成功像素 `(4,4)`、后帧、既有串口和 QOM 内容断言继续使用原规则。

旧 runner 在 load 10.064–18.438 时两项全黑失败，最终两个目标案例在 load 6.727–8.680 时首轮通过。真实超时负控以非零退出，保留零非黑像素的失败帧。早期修复的触摸时序、校准与部分绘制失败继续留档。最后一次 warmup 为 3.389–7.688，低于 10.0 门槛，8 个负载进程全部退出，该轮 guest 为 `NOT RUN`。两轮各 68 项高负载无重试验收仍待执行。[外设帧和负载证据](evidence/peripheral-readiness-summary.json)

## #193 实际运行时证据

原来的 batch12b 结果只保存会话哈希，共享 finalizer 无法用其查询活跃证明。控制与传感器 runner 缺少统一写入。修复在 QEMU 仍运行时采集实际进程可执行文件的 SHA256，并复核会话固件、worker generation、租约和 PID。batch12b 以显式会话索引查找已观察的证明，结果保持哈希标识。配置哈希与实际执行哈希不同时输出 `FAIL`，有功能结果但缺少可验证证明时输出 `PARTIAL`。[故障描述](https://github.com/m5agent/m5stack-esp-emulator/issues/193)

CoreS3 的 batch12b 7 项、control 5 项、sensor 7 项合计 19 项均 `PASS/VERIFIED`。实际 QEMU SHA256 为 `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`，基线固件 SHA256 为 `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded`。每项记录独立的合成镜像、同会话 ZIP、功能输入/输出、帧和串口。19 项探针文件与历史记录相同，14 项合成镜像也逐字相同。真实 BMM350 负控使用全零的 expected SHA，功能断言仍满足但结果为 `FAIL`、退出码 1、分类 `runtime-provenance`。会话历史保留，全部租约释放，验证服务退出码为 0。[运行摘要](evidence/unit-runtime-summary.json)

两次前置启动均未创建 guest。第一次缺少该隔离环境要求的 esp-emu 可执行文件，第二次端口尚未重新可用。第三次完成 19 项和真实负控。执行提交为 `db535de07bfd3dda673678cd556b6f60f2cb8d29`。整合对比中九个声明路径哈希相同，共享 `run_profile_ui_test.py` 的差异仅为 direct QEMU 截帧函数和 CLI `main()`，Unit 路径导入的构建及通用帮助函数保持相同。[源码绑定](evidence/unit-runtime-source-binding-summary.json)

## #178 ROM stub 上传恢复

用 AtomLite 的跟踪矩阵重现了 `MEM_BEGIN` 应答已到达、stock stub 尚未发出 OHAI 时的 RAM checksum `0107`。同一镜像在默认 pacing 16 再次失败。提交 `9214bfaf62bf7ea0117fd0256463ae4c0eb3bae2` 保留首次协议失败与 UART SHA256，在该类已确认失败或对应 stream-stop 后使用新的 ROM 虚拟机和全新虚拟 Flash，以 pacing 8 重试一次。重试获得剩余请求时限。现有 OHAI 和逐字节 Flash 回读仍是成功条件。

esptool 5.6.0 下，AtomLite 的 pacing 8 重试得到 OHAI。镜像与读回均为 `45daa932641e35a5fef15d6ce22a69539606a12baadde77223d64f909a6ba7d3`，guest 给出启动、板识别和 RGB 标记。Core2 与 StickC 独立烧录在 pacing 16 通过。隔离 Device Service 的 AtomLite 冷 qemu-esptool 也在 pacing 16 完成完整读回、按钮两沿、ZIP、历史保留和进程清理。另有独立 host-image 对照。pacing 8 在 load 12.014–27.966 的一次对照读回通过。Basic pacing 1 的两次 OHAI 后失败保留为其它协议阶段的负控。完整重复高负载 Classic 矩阵仍待验收。[Classic 证据](evidence/classic-flash-summary.json)

## #188 与交付边界

上游正式版本核对为 esp-emu 0.51.0。现有 Tab5 DSI PHY 阻塞继续跟踪，官方固件重跑为 `NOT RUN`。[上游发布](https://github.com/espressif/esp-emulator/releases/tag/v0.51.0) · [#188](https://github.com/m5agent/m5stack-esp-emulator/issues/188)

完整平台 R1 运行 2039 项，用时 146.212 秒，10 项跳过。唯一失败是新 evidence 缺 freshness-index 行。修正索引后，最终提交的 R2 运行 2039 项，用时 129.987 秒，2029 项通过、10 项跳过。文档 50 项、Node 30 个脚本、离线 Unit evidence 68 项、四项 validator 与 PR scope 均通过。scope 为 37 个新 blob、3,479,320 字节，新增源码证据 126,271 字节。源码 PR、合并及 issue 关闭结果随交付另记。[验证汇总](evidence/summary.json)

#190、#191 为静态官方资料核对。#178、#192、#193 的实测均为 `virtual-device validation`，按各自路径保留固件、输入和清理证据。物理硬件及部署属于 `NOT RUN`。
