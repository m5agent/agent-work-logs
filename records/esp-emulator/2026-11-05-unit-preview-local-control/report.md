# 实现与限定验证

## 改动

独立 Unit catalog 模型与主设备装配共存。切换、关闭、重开和晚到模型加载都有所有权栅栏；
主机运行/加载时，当前或后来创建的预览渲染器使用相同暂停/恢复流程。
预览与Add是两个动作：只有Add改变草稿；查看已有会话时预览操作不写会话。

服务端原先在配置缺省时允许旧local-control API，却对Preview无条件返回503。
新增请求上下文helper只替换Preview的这个门槛，保留原owner、CAS、payload、body错误与生命周期契约，API版本1.51不变。

| 情况 | Preview规则 |
| --- | --- |
| 已配置current/previous认证值 | 仍须原认证；本机也不绕过 |
| 未配置且监听/peer均loopback | 还需严格Host、实际端口和请求来源校验 |
| 浏览器带Origin | 精确匹配实际scheme/Host；null/跨站/不同端口/重复头拒绝 |
| 同源GET没有Origin | 有可信同源上下文时可读 |
| 本机CLI无Origin与Fetch Metadata | 在上述socket/Host边界内可用 |
| Node fetch仅mode=cors、无Origin/Site | 不算同源证明或无metadata CLI，仍拒绝 |
| 远程peer、宽泛监听、DNS名称或伪造Forwarded | 不获得本机例外 |

拒绝无配置请求仍为 `preview_auth_unavailable` 503，配置过认证值时缺失或错误仍为401。
helper不解析DNS、不信任代理头；跨站或矛盾来源先于Preview body解析与分配拒绝。
该范围不构成所有旧Device API的CSRF沙箱或多租户隔离。

## 执行证据

- host20通过：独立真实模型、Add幂等、晚到加载销毁、切换设备不污染草稿、已有会话点击不写入，4宽度无横向溢出。该轮0 guest/Worker/WASM请求。
- 原生14通过：隔离、无手填认证值的CoreS3+PIR。同VM三程序、原PIRUnit true/false、实际红绿帧、导入与取消均核验。8个实际浏览器POST自然Origin精确同源且没有Authorization；Fetch-Site在观察中均缺失，没有伪造此头。
- CLI观察器使用原始HTTP且无Fetch Metadata。最终pre-stop产品Blob ZIP为33,844字节/25members，CRC、成员哈希及三程序身份通过；网络body观察仍0字节，这一缺口保留。ZIP验证经原JSON的文件描述符输入并有10秒边界，不降低原断言。
- 浏览器65通过：PIR独立模型在CoreS3完整运行前后保持同一个实例，但主机模型附着数0、草稿为空，未绑定PIR控制器。原12个raw-paste程序和2次默认代码全部保留，包括真实红帧、中断、硬重置及恢复。

原生QEMU SHA为 `6d9af027e2f744208fc2503128f1772f436d7ca7358f9e53be597bc76800f39d`，Flash为 `0ede40601c1e37b7ba32c87a3ca55e4da7a448f6cf52957f005763bc7c7c78e8`。
其配置为host-image准备的虚拟Flash，最终运行复用cache，并未验证esptool串行传输。
浏览器使用WASM `96ea9f91956aa80926182ed174ea426f3f4c84e96ca58754fa249063fdda5ca1`，
Flash `52f38f562f6e3749357a2ed4834efd72d16870046ea052f2f31691743cb5384d`，静态manifest `23ee838732c99369d2b0b852b4430c46eee48236ed768a88d9374a5969cc8b2c`。

原生UI停止后PID退出、lease和活动会话为0、历史保留、可变Flash释放；测试浏览器关闭。
浏览器正常QMP退出0、forced/fallback为0，iframe前及context前两次CDP均观察6/live0，owned浏览器与静态服务关闭。
这两个运行路径不能互相转授外设、性能或固件验收。

## 保留的失败

第一次native观察器误用默认Node fetch：产品浏览器无Authorization的Preview POST已202并ready，
后续CLI观察器却带mode-only Fetch Metadata而503。独立CLI取证和关闭完成，原FAIL不重分类为guest失败。
第二次已完成原11项实际功能，但同步ZIP管道验证器无界挂起，需终止拥有的观察子进程；
同时要求Fetch-Site必须存在也是观察器过约束。最终改用自然Origin证明、原始HTTP观察器和有界文件描述符ZIP传输。
原报告的字节数/SHA、各次harness身份和清理保留在native摘要中，不用最终PASS覆盖旧FAIL。

## 检查与未部署边界

28项auth方法已通过，包含实际HTTP configured认证、bind/peer/Host/Origin/Fetch Metadata和body/分配先后负控。
最终源码为 [22001fe1cb6bb44eb2737872e4cc578605e57921](https://github.com/m5agent/m5stack-esp-emulator/commit/22001fe1cb6bb44eb2737872e4cc578605e57921)（base `082fffafd124800564d11c82b56cc4ecbb2c503d`）。客测摘要所列源码逐文件与该提交相同。

最终全量Python运行1986项/136.687秒，1976通过、10跳过；Node30、文档50、4个验证器、scope和diff检查均通过。首次全套唯一失败为inventory引用旧contract哈希；operation集合未改变，更新1.51契约身份后完整重跑通过。这是保留的metadata失败，不是guest失败。

静态包精确闭集2134资产/251,980,691字节，manifest `23ee838732c99369d2b0b852b4430c46eee48236ed768a88d9374a5969cc8b2c`；归档147,128,260字节/SHA `e56d7e9faeeea1ff4cd651b51fc8ab366208b94502362f2d576ba0a5e75f695b`。无固件打包、服务URL为空。包检查不等于部署。详见[最终摘要](evidence/final-validation-summary.json)。

PR、Pages与现有用户Python进程更新仍为PENDING。未在现有用户服务部署或重启Python，不应把隔离测试结果写成该服务已升级。
无新HTTPS、全19板或其它Unit验收；原runtime故障、物理属性和性能均不由此关闭。

## 复现与回滚

在固定提交上运行auth合同：`PYTHONPATH=platform/tools:platform/tests python3 -m unittest test_preview_request_context test_preview_http`；完整平台及Node命令列在最终摘要。原生和浏览器的固定镜像、测试脚本身份与具体行为见各自bounded摘要。原生需独立服务状态与已准备的兼容Flash，浏览器需固定WASM静态导出；不复用用户会话。

回滚源码提交可撤销本次模型和Preview请求入口变更；服务端Python需受控进程更新才能生效。回滚与部署均未在本记录执行。
