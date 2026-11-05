# ESP Emulator 统一 Web 工作台报告

## 背景与目标

用户观察到主界面没有可用的 UIFlow 编辑器、Unit 浏览区只能查看模型，而实时会话控制台可以装配 Unit。
目标是在主工作台完成设备选择、Unit 装配、代码运行、取消和已有会话查看，并让静态导出与服务页面使用同一前端实现。
本记录覆盖公开项目的功能修订，排除私人服务配置和内部运行环境。

## 已定位的原因

1. 旧服务启动树仍使用 `b41eba70eb61f7ddc5c41e0b981341064f9d1d1f`，与工作台新源码版本不同。
2. 同版源码也存在执行分支差异：服务端为站点配置提供所选服务地址；自动模式优先原生服务，静态站点可使用浏览器内核。
   原首页编辑器仅接受浏览器 QEMU 对象，原生会话被明确排除。更新页面版本本身不足以接通原生编辑器。
3. 独立 Unit 浏览区只提供模型查看；实际 Unit 选择器与会话面板在另一入口中。Unit 连接在创建时冻结，已有后端不提供运行中热插拔。

## 实现与兼容范围

- `public-service-program.js` 复用现有 Preview/Run、不可变 revision、取消和停止 API，不在主机执行用户代码。
- `PublicSessionController` 可接入 managed 会话，Unit、按键输入和帧使用同一 Preview 上下文；帧同时校验 Run、execution、revision 和实际内容摘要。
- 新建会话的取消在分配收据未知时保留原始创建意图，只为恢复身份使用同一创建请求；不自动重试代码 Run。
- 仅初次、明确发生在分配之前的两类认证拒绝可以退休创建意图；其它错误与恢复请求仍保留未知结果。
- 已有会话接入不获得生命周期所有权。普通 UART 编程会话使用原 `/program` 及 `expected_execution_id`；独立中断不可用时不显示虚假的中断能力，运行中可用 CAS 替换代码。此旧会话分支目前有 host 合同，不能从新 managed guest 转授真实运行通过。
- Unit 草稿只负责接线和外观；实际输入/读回来自本次会话。实际会话没有 Unit 时，不将草稿装配伪装为该会话的外设。
- 原浏览器 raw-paste、手动 UART 与中断实现保持原路径。主页面增加每次 Run 的显示栅栏，旧操作的晚到输出不覆盖新代码。

后端当前能力声明与实际验收是两层。Preview 与普通 UIFlow-live 使用同一主机集合；
适配器读取实际服务声明，不从浏览器准入或静态模型推导原生执行能力。

## 审查中发现并修正的边界

- 已查看 A 时先请求 B，再点击 A：旧快速返回未撤销 B 的在途打开意图。快速返回现会推进打开代际。
- 设备选择中的异步 Unit 装配返回后缺少选择代际复核，旧选择可能清空新模型。新增 await 后的选择栅栏。
- 明确拒绝创建被当成未知分配，导致停止恢复重复提交必拒请求。限定到源码证明的首次前置拒绝，不扩大为一般错误跳过。

这两处页面竞态均由最终 Chrome host18 反例覆盖；其输入为明确标记的生命周期 fixture，不能替代 guest 验收。

## 执行与证据

已完成的纯 host 命令：

```sh
node platform/tests/test_public_service_program.mjs
node platform/tests/test_public_session_controller.mjs
node platform/tests/test_preview_client.mjs
node platform/tests/test_public_micropython_ui.mjs
node platform/tests/test_public_micropython.mjs
node platform/tests/test_public_config.mjs
```

adapter 15 项控制通过；原控制器合同、PreviewClient 25 项及浏览器编辑器/UART 合同通过。
这些命令使用确定性的协议 fixture，不能证明真实固件、Unit 协议或设备输出。
Unit19、Node30 个合同脚本和 Chrome host18 已通过；Chrome 四次 observer FAIL 及中间17项 PASS 均保留。
最终前端副本 `e0f60211ab05f9c558833a825430d489a9900db672c62eb47c464d97ab323bcc`另获 host18 PASS；
报告3768字节/SHA `e11b91740bac29c25b1368a42acd9be355b5a1daba76be010390563fc4eda6fd`，不覆盖上一轮同项数的独立结果。
两次全量 Python 均运行1973项，分别因旧导航/日期登记及当前日期/行数/动态快照断言出现2个元数据失败、10个跳过，原日志身份保留。
最终 `e31c2b4aed07c98fddea19018589f0f8751667c2` 同源码全套1973项于145.507秒完成：1963通过、10跳过、0失败；
Node30脚本、四生成器、diff与分支范围检查全部通过。源码范围34 blobs/1,404,889字节，新增 evidence26,157字节，无范围错误。

首次 native 检查在 backend/program 能力前提失败；第二次在隐藏的运行方式选择器上等待超时，
尚未进入程序或输入检查。两者分别属于前提与 observer 层，不写成被测固件失败。
原报告仅以字节数和 SHA256 引用，不复制环境字段。
r3 缺少必要固件工具，r4 使用的工具版本4与服务预期的版本5命令不兼容；两次均未进入 QEMU guest boot，清理已确认。
环境按版本5.1.0另行准备后进入独立跟进；这两次属于工具前提失败，不归类为产品源码或固件失败。

## 限定真实虚拟设备验收

原生 CoreS3+PIR 最终13/13通过，UTC01:56:51.920至01:57:05.533。Flash `0ede40601c1e37b7ba32c87a3ca55e4da7a448f6cf52957f005763bc7c7c78e8`，
原生 QEMU `6d9af027e2f744208fc2503128f1772f436d7ca7358f9e53be597bc76800f39d`。
Run A/B/文件导入保持同会话/PID/固件，PIR motion true/false 同时有真实 QOM 与官方 PIRUnit.get_status 串口1/0，
主模型显示320×240红帧和绿帧；同次 Preview cancel 确认 cancelled。
产品已有 lastEvidence Blob 是 UI 停止前取得的 ZIP，33,819字节、25 members、CRC与全成员大小/SHA及三程序身份核对通过；
网络 body observer 仍返回0字节，这一观察缺口保留。停止后历史保留、PID退出、lease释放、活动会话与lease均0、可变Flash释放。
原生 argv 没有单独捕获，已有标准工具准备的缓存被复用，不能称新工具传输验收或性能测量。

r5 的 observer 错用30秒等待而非已授权120秒，在 QEMU未启动时误截；报告时清理尚未确认，随后独立确认 stopped。
r6 已有11项真实功能通过，但网络 body ZIP 观察为0字节，未捕获产品 pre-stop Blob；后取 API ZIP 仅为诊断，不追授整轮 PASS。
r7 的13项完整结果及其 pre-stop Blob 独立成立，不覆盖 r5/r6。

浏览器 CoreS3 完整63/63通过，UTC01:57:59.371至01:58:27.410，项目子路径导出 manifest `23e3fc8515b0f02b585bce0eb36e4e9f6579113d03ba96c6aafc12680f61844c`。
Flash `52f38f562f6e3749357a2ed4834efd72d16870046ea052f2f31691743cb5384d`，WASM `96ea9f91956aa80926182ed174ea426f3f4c84e96ca58754fa249063fdda5ca1`，
divisor1、无override、实际 TCG multi/one-insn-per-tb，精确0027绑定。
12次 raw-paste 包括2次未修改默认程序、UTF-8/长源码、异常、导入、无限循环中断、同VM恢复、真实红屏和硬重置后运行。
正常 QMP退出0，forced/fallback均0，iframe保留前nested及context关闭前全部两阶段均观察到6个实际 CDP targets且live0。
该轮没有新增外部 Unit，也没有原生 API 请求，不能转授 native、HTTPS或完整设备矩阵。

## 最终源码与准备包

最终源码为 `e31c2b4aed07c98fddea19018589f0f8751667c2`，parent/base为 `3e8f76b836009438b7d9312e1e7b8f822b7d64f5`。
回读提交内20个 native/browser摘要绑定的源码文件，SHA全部相等；不把旧准备快照冒充最终源码。
最终准备包147,130,306字节，SHA `73f87c9bbdc09d1d885df1bf2f538cca3cfa8da078c5d086124deb96e5c80353`，
包内2,134资产/251,977,755字节逐项核对 manifest闭集，不含固件/ROM和私人服务配置。
首个打包因额外 AppleDouble metadata 被闭集反例拒绝；设置 `COPYFILE_DISABLE=1` 重打后的独立最终包才通过。
此为包装完整性，不能替代部署或 HTTPS guest 验收。

## 验证结果

| 层级 | 当前状态 | 依据与范围 |
| --- | --- | --- |
| review | REVIEW | 已定位入口差异并审查新旧执行分支 |
| build | PASS | 前端合同与静态包闭集通过；本次未重建 QEMU |
| transport | PASS | 精确 native UART同VM和browser raw-paste限定路径 |
| device_response | PASS | native官方PIR读回、Run/取消；browser真实MicroPython结果 |
| data_behavior | PASS | native PIR true/false及三程序身份；browser12程序与reset恢复 |
| visual_or_physical | PARTIAL | native红/绿帧与browser全红帧来自guest；物理性质NOT RUN |
| delivery | PARTIAL | 源码与准备包已固定；PR/合并/Pages仍PENDING |

## 验证边界

静态站点仍不包含原生服务，统一的是前端工作流与能力呈现，不是把服务端功能复制成浏览器外设模型。
未知固件和未声明主机不继承编程能力；Unit 热插拔、物理电气、RF 和性能不属于本次通过范围。
先前运行时 reset/PIF 故障没有因页面改动而关闭。

## 风险与回滚

本次修改使用既有服务端编程机制，不涉及物理设备写入或运行时重新链接。
回滚应恢复最终源码提交中的前端适配与入口变更，并保留原生会话历史；不能把页面关闭当成 guest 已停止。
guest 镜像/runtime、逐文件SHA、最终源码与完整检查均已固定；PR、合并、Pages及新HTTPS结果须以独立后续记录追加。
