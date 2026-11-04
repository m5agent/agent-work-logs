# ESP Emulator 浏览器启动调查报告

## 背景与结论

用户要求优化全部19款浏览器可运行设备的启动和按键，默认UIFlow并增加MicroPython编辑器；其余型号保留能力边界。本记录只封存当前正式运行时的慢启动调查，整体状态PARTIAL。

固定基线使用原公开源码 `b41eba70eb61f7ddc5c41e0b981341064f9d1d1f`，原producer `1b86ed6f7edcc36deafc4834b45a28c6a6017c79`，QEMU `40edccac415693c5130f91c01d84176ae6008566`。WASM为 `3c6b249002d83118e0ddcbd82e4ee6336223293b98566fc7709d5087d9df4567`；正式站点manifest `c5991d737d4b20c4b1ae96b71587cec907a1e72f3c57fe2fee63c08e23daf323`。Flash、ROM、JS、Worker、实际参数和完整源文件身份见JSON。

## 实际执行

| 运行 | 观测 | 验收边界 |
| --- | --- | --- |
| Atom Matrix原icount5固定示例 | ready109.458s，15/15 | 原USER键、RMT/QOM/模型与正常两阶段Worker清理 |
| 原StickC Plus固定示例 | ready90.687s，26/26 | 仅BtnA、frame/纹理、暂停恢复及正常Worker清理；不授B/PWR |
| Matrix MTTCG+oneInsn | ready前cache访问panic | 首FAIL保留，输入/稳态/warm NOT RUN，正常CDP清理未捕获 |
| Matrix原single/icount5+oneInsn | ready126.620s，无性能收益 | 前面真实输入/RMT检查通过；旧observer错误要求墙钟8秒内两次虚拟心跳而FAIL，未重写原报告，正常CDP清理未捕获 |
| 独立早启20秒CDP | engine及四pthread采样成功，Stop/CDP清理通过 | 有剖析开销，非CPU利用率，未覆盖后段Python导入，未知wasm索引未命名为C根因 |

最初使用已撤回的旧 `0bd94787…` 的三轮测量已标为DIAGNOSTIC_OLD_RUNTIME_SUPERSEDED，不作当前Pages基线。上述两板均已在正确3c重新执行。

原WASM没有name section。仅添加--emit-symbol-map重链接得到另一个WASM及不同索引，未将其map套给3c。本阶段未接受oneInsn配置，也未声称之后的0030候选有guest收益。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | REVIEW | 使用已发布source-built3c；新候选构建不在本记录完成范围 |
| transport | PASS（限定） | 两板同guest UART/QMP输入及输出 |
| device_response | PASS（限定） | Matrix USER、Plus BtnA实际原驱动响应 |
| data_behavior | PASS（限定） | Matrix RMT/QOM，Plus帧与计数；全部按钮未验 |
| visual_or_physical | PARTIAL | 同guest模型/帧通过，物理硬件NOT RUN |
| delivery | PARTIAL | 调查归档；新功能、提速及部署未完成 |

## 复现与可追溯性

从[固定源码](https://github.com/m5agent/m5stack-esp-emulator/tree/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f)的独立checkout，按[部署说明](https://github.com/m5agent/m5stack-esp-emulator/blob/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f/docs/pages-deployment.md)准备原3c完整站点。对应包来源为[原发布](https://github.com/m5agent/m5stack-esp-emulator/releases/tag/pages-performance-20261103-10788607)，使用前核对JSON中的完整hash，不能替换新构建后继承本记录。

以独立ignored输出运行 `platform/tests/test_public_qemu_headless_guest.mjs`（M5_QEMU_DEVICE=atom-matrix）与 `platform/tests/test_public_qemu_board_guest.mjs`（stickc-plus）；共同参数为M5_PUBLIC_SITE指定对应导出、M5_PUBLIC_BASE_PATH=/m5stack-esp-emulator/、M5_PUBLIC_UI=1、M5_WASM_GPU=hardware、系统Chrome。附加计时/CDP observer的脚本和原始报告只有哈希/尺寸在本摘要；既有功能入口不自动产生其附加计时/profile。性能依赖访问者硬件与环境，单轮结果不构成延迟分布或保证。

## 风险、回滚与后续

没有变更用户常驻服务、没有物理硬件操作、没有部署新站点。未采用的候选只在隔离诊断出口；正式配置保持原样。后续新运行时、新默认Flash、全部19款按键和源码执行必须重新逐板绑定输入、串口、frame/QOM与正常Worker清理；这些工作保持进行中。原始大报告、帧和profile留在ignored存储，公开归档只保留有界派生证据。
