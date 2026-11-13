# 原生模拟器时钟、USB 串口与原版固件补充验证

- 日期：`2026-11-13`
- 结果：`PARTIAL`；已验证的交付与复验范围为 `PASS`
- 工作类型：`issue`
- 问题来源：[经典 ESP32 启动与时钟 #225](https://github.com/m5agent/m5stack-esp-emulator/issues/225)、[C6 原版固件边界 #216](https://github.com/m5agent/m5stack-esp-emulator/issues/216)、[StackChan 原版稳定性 #223](https://github.com/m5agent/m5stack-esp-emulator/issues/223)
- 源码：`m5agent/m5stack-esp-emulator`；实际执行源码分别为 `1be1e1464a49e7e36d849a4610cac6eacfc91ac4`、`a8c9b222c6af0081fd48bc7facafa7cd12b6e5c3` 、`10c826b832b78c9bc42e9f788bd3e595584978ae` 和 `4a5d28e6d4764ec78c0621aed0e0527080597486`。每项绑定见 [run.json](run.json)。
- 环境：Apple arm64 主机、原生 Xtensa/RISC-V QEMU；使用原生 Device Service 独立验收会话（早期隔离实例及最终获授权常驻服务），网页连接同一原生虚拟设备。不是浏览器 WASM 或物理硬件验证。

## 结论

原版 JIGGLER 的两轮有界自适应及一轮固定时钟按键路径通过；NanoC6 原版 Honeypot 的完整配置串口输出、独立串口通道 API 和三个页面切换通过。C6 的 USB、TSF、身份控制及限定的 Nesso 原版界面路径有各自证据。整体仍为 `PARTIAL`：完整无线应用和部分原版故障仍有明确边界。最终 69 项环境常规负载矩阵、main 交付、两个常驻服务和部署后验收现已完成。共享中断修正后的 80d 产物已有独立定向及页面证据，旧 8df 结果保持历史身份。

当前公开目录中的 UserDemo、GPT 和 RFID 三份 BIN 经重新下载计算哈希，均与先前验证的原始文件相同。这是文件身份核对，不是新的运行结果。

## 关键证据

| 范围 | 已完成结果 | 证据 |
| --- | --- | --- |
| JIGGLER 1.0 | 两轮主界面后的虚拟时钟下界均超过 300 秒，默认轮设置页后的下界为 15.866 秒；正常看门狗、原应用字节不变 | [输入、时钟与画面摘要](evidence/jiggler-bounded-adaptive-summary.json) |
| Core2 / Plus2 | 固定与有界自适应共四条显示和输入路径 | [四组合摘要](evidence/classic-input-regression-summary.json) |
| NanoC6 API / 三页面 | 同一原版 guest，461 字节 console 与 614 字节 USB 分开；完整 153 字节应用输出；18 次 API 与 13 次页面响应核对 | [串口页面摘要](evidence/serial-channel-ui-summary.json) |
| C6 `8df53714…` | 五个控制探针及限定的原版输出/界面行为；保留失败和缺口 | [共享中断修复前摘要](evidence/c6-pre-shared-irq-runtime-summary.json) |
| C6 `80d92a6c…` | 0023 共享 pad、五探针、原 Mesh/Bruce/Honeypot 与两项回归；按各自范围通过 | [新运行时定向摘要](evidence/c6-final-v3-runtime-summary.json) |
| 新运行时三页面 | 独立原版 guest 90.012 秒，18 API / 13 页面响应，九张截图；保留前次窗口结束失败 | [80d 页面摘要](evidence/serial-final-v3-ui-summary.json) |
| 当前公开 BIN | 三份文件与原始测试文件 SHA-256 相同 | [下载身份摘要](evidence/current-artifact-summary.json) |
| 宿主检查 / CI | 本机 2,177 项、8 项跳过、退出 0；首次 Linux CI 失败后修正三个 GCC harness，后续 CI 成功 | [检查时间线](evidence/host-and-ci-summary.json) |
| 新源码检查 | `4a5d28e6…` 本机 2,178 项、8 项跳过；分支 CI 43446583704 和 main CI 43453074487 成功 | [4a 检查摘要](evidence/host-and-ci-4a5d-summary.json)、[交付摘要](evidence/post-delivery-summary.json) |
| 最终联合矩阵 | 5ce / 80d、69/69、每项一次、无负载 worker，已清场；不作高负载认证 | [环境常规负载矩阵](evidence/ambient-matrix-summary.json) |
| main / 常驻 / 发布后 | 精确 4a、两个服务；九个独立首轮用例，原 MP3/2048 dry-run 通过，11 个会话已清场 | [交付接受门](evidence/delivery-acceptance-summary.json) |

[报告](report.md)说明根因、变更和验证边界；[运行时身份](evidence/runtime-pins-summary.json)和[来源清单](evidence/source-evidence-manifest.json)保存完整 SHA。`patches/`、`code/` 在本补充记录中不适用：可重建代码和补丁已由报告中的固定源码链接提供，不重复复制第三方源码。

## 已交付范围与保留边界

[精确 main 提交 4a5d28e6d4764ec78c0621aed0e0527080597486](https://github.com/m5agent/m5stack-esp-emulator/commit/4a5d28e6d4764ec78c0621aed0e0527080597486)及其 [main CI 43453074487](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43453074487)已成功，两个获授权的常驻服务已部署 Xtensa `5ce7d9f…` / C6 `80d92a6c…`。旧历史与配置保留；九个部署后独立首轮用例和两份原版 dry-run 的全部 11 个测试会话均已停止并释放 Flash、租约和进程。[最终接受门](evidence/delivery-acceptance-summary.json)是当前状态；[部署前门禁](evidence/pre-delivery-gates-history.json)仅为保留的历史，不能当作当前未交付。

原 MP3 的实际 PCM 524 Hz 控制、原 2048 的八次方向移动及 merge/spawn 规则通过独立机器复算与帧复核；两份原应用区域字节不变。审核服务的 `SIM_VERIFIED`、原 helper 的 `REVIEW` 和另行人工复核分别保存，未回写旧状态。Burner 未提交。

首轮 Linux CI 的三个编译错误、原版失败、Mesh 的 B 键预期失败、首次 Observatory 外部观察器失败和 80d 第一次页面窗口衔接失败都保留。部署后原版审核首次因缺少 Pillow 在进入队列或创建 guest 前失败；使用已有依赖路径后重新执行，helper 字节未改。最终审计器还保留错误日志定位和整数类型处理的两次自身失败；它们不归为固件或产品故障。本轮九个 post 用例均为独立首轮，无旧 cloud 结果复用。

Honeypot 的 AP 关联与 HTTP、BLE HID 空中传输、物理时序和浏览器 WASM 不在通过范围内。现场回滚、状态迁移及部署前令牌字节相等性没有执行或没有基线；57 项隔离宿主控制不等于现场回滚。本记录保留各执行阶段的独立身份和结果。

后续文档主线已更新到 [ffa621cdcf8422005b7fdf66afdee1be7c5fbba7](https://github.com/m5agent/m5stack-esp-emulator/commit/ffa621cdcf8422005b7fdf66afdee1be7c5fbba7)。从执行版本 4a 起只追加或更正文档与有界 JSON 证据，常驻服务仍固定在 4a；[差异核对](evidence/final-documentation-main-summary.json)没有把新文档 SHA 当作重新执行结果。
