# C6 GPIO IRQ 修复报告

## 背景与根因

实际输入已经到达 GPIO pad，但旧模型没有普通中断的 pending、逐 pin CPU mask 和输出连接。
Patch 0024 在 C6 子类中补充 STATUS、PCPU_INT、五种触发模式、W1TS/W1TC、复位语义，
接入既有 source 30 中断矩阵。Nesso 的主 PI4IOE 和触摸继续共享 GPIO3：确认一源时，
另一源仍有效则不能错误释放 pad。未新增 Python 假值、直接调用 ISR 或主机计数替代。

## 固定产物

| 产物 | SHA256 |
| --- | --- |
| 新 C6 runtime | `69493c4edccaab5bc24961982ddb9097dda11c9b3418f9cdc0aaa2b27ae865a4` |
| 旧 C6 runtime | `80d92a6c6c68137a7813b8b7c519725aac350258078d9b244098eaabf82f63bf` |
| C6 ROM | `91db14c2419391308b108bac0b15fe3442a9c411cdd7f3fb088767c9fbc4b713` |
| NanoC6 IDF 镜像 | `2a0e22623387a60c339eb075d12e39f2b674bb04365a1be41d9bf16582e5ca4c` |
| Nesso IDF 镜像 | `316e46505f1d88bb652aedbd6e4557926fc1b6da35e32d767cd5a234f08ed83a` |
| 原版 Nesso UIFlow v2.5.3 BIN | `fcbd588fa92bcd24c8d4ba8fcd8837b8df64a6d5be72771e520c1ed84af88c7a` |
| Service VFS 合成镜像 | `16255a35d2142a7f68363c79d3a083bab207e6c104b6a91d3563f8646889a3aa` |
| 保留的原版 app 分区 | `4743d8b5e3cf234b064dc01566fa1cce9e44b545ea72992081a2628b937a6ba4` |

IDF 固定版本 `735507283d5b2f9fb363a1901172dbd9e847945d`，27 个递归子模块，
每板解析 55 个组件、编译 556 份源文件、记录 1,614 项源码/头文件依赖。
先前缺 MQTT、mbedTLS 的两次配置失败属于构建基础设施失败，未转记功能 PASS。

## 实际输入与结果

| 验收路径 | 旧 runtime | 新 runtime | 实际观测 |
| --- | --- | --- | --- |
| NanoC6 IDF / GPIO9 | FAIL 12/21 | PASS 21/21 | source30 路由 CPU interrupt10；五种模式、禁用/保持、level mask/rearm、复位 |
| Nesso IDF / GPIO3 | FAIL 14/26 | PASS 26/26 | source30 路由 CPU interrupt11；另含按钮/触摸共享源确认与释放 |
| 原版 Nesso UIFlow / GPIO3 | FAIL 20/32 | PASS 32/32 | 22 次实际输入、1 次 reset、两轮各16检查；每轮回调上限旧0/新6 |
| checked-in portable Nano runner | 未重复旧控 | PASS 21/21 | 与原私有 runner 的实际序列/断言相同，显式传入产物 |
| checked-in Nesso matrix case | 未重复旧控 | PASS 16/16 | 11 次 marker 顺序输入、USB 控制台、135×240 绿色结果帧 |

同板 IDF 旧新输入序列完全相同，四组均两次 READY、一次请求 reset、无 fatal marker，
QEMU 进程和 UART reader 线程清理成功。UIFlow handler 是 callback 计数唯一增量来源；
Pin/I2C 读取只用于同步/确认实际源，不代替中断断言。触摸保持 0.5 秒，未放宽时间或断言。

VFS 原有17文件中保留15，替换 `boot.py` / `main.py` 并加入 `irq_probe.py`。
所有 VFS 外字节不变。app 分区偏移 `0x10000`、大小 7,405,568 字节，运行前后均与原版相同。
因此这是“原版可执行代码 + VFS fixture”，不能称整份 BIN 字节不变。
两组 Service 在 stop 前取得 ZIP，八项清单文件均验字节数/哈希；保留历史 `purge=0`，
释放 guest、lease、mutable Flash 及所属服务。初次缺 flash-emulator 路径的预检失败无 guest，单列保留。

矩阵合成时还加入未导入的公共 `rtc_probe.py`，故其镜像单独绑定
`623a45423230352e354eb2f6c2f5c2bc1f7bec8472c9f9149ade3e4f4981ad42`。
最后一次明确设置 Nesso board；先前使用默认板选择的 PASS 作为独立历史保留。

## 来源、复现与边界

用固定源码内 README 的构建和运行命令复现；portable runner 必须显式提供 runtime、ROM、
镜像、build receipt、输出目录及 `--execute`。普通原版 UIFlow 应用验证使用可见 Service session；
IDF 采用已登记 UART 回归路径，其 Service lane 没有运行。

UIFlow service 相关86个源文件在执行后对两份 Git 提交核对一致；基线运行期间仅5个测试
文件发生 cherry-pick。这里保留事后绑定事实，不改写为预先冻结的运行。服务 QOM 快照在
Nesso board children 之前被截断；GPIO/intmatrix 可见，行为由实际输入与固件 Pin/I2C 确认，
不声称完整 board tree 已导出。三份 fixture 与受审 Git 文件逐字节一致。

## 分层验收

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | 固定源码/工具链/产物 receipt；不完整 SDK 历史失败另列 |
| transport | PASS | 相同实际 QMP/UART 输入；Service 输入与 USB 控制台 |
| device_response | PASS | 原固件注册的 ISR / Pin.irq handler 执行 |
| data_behavior | PASS | 旧新对照及禁用、保持、ack、reset 控制 |
| visual_or_physical | PARTIAL | 虚拟 framebuffer 红/绿结果帧通过；物理硬件未运行 |
| complete native matrix | PASS | 后续实际70/70，逐case一次；独立复核70份app、422产物、70组帧、77离线解码 |
| delivery | PASS | 修复已合入最终 main，同提交两项 CI job 通过，最终源码功能复验 32/32 |

## 风险与回滚

普通 GPIO 修复不覆盖 NMI/source31、睡眠唤醒/滤波时序、BMI270 IRQ 或 FT6336 脉冲时序。
此记录不宣称浏览器 WASM 或物理电气行为已验证。旧独立 runtime 保留，替换回旧
运行时会重新出现已复现的 IRQ 缺失；生产回滚只能使用另行审查的精确资产/空闲 ownership
流程。完整矩阵现已追加独立 execution；原版 Mesh/Bruce/Honeypot 限定非回归见下方独立 follow-up，不重写初始失败。

补充独立复核见 `registered-case-independent-audit-summary.json`：两次矩阵各16个计数、11个marker步骤、12个实际QMP输入（触摸含按下/释放），以及portable Nano21/21再次与原始数据核对。矩阵显式板型来自case源码和调用记录，原始报告未保留独立进程环境快照，不宣称拥有该快照。

## 完整矩阵 follow-up

实际执行源码 `0e00cdcbc99a8210af6485df1bcfd04a514bc8a1`，70/70、每项1次、0重试。
其中64项使用既有 Xtensa runtime，6项使用新 C6 runtime；不能称70项都运行在C6上。
11份原始BIN、5个ROM、两份native runtime、523个相关实现文件及5643个preflight源文件均绑定。
与整合候选的523个实现文件逐字节相同；后继候选只有18项docs变化，不把实际执行HEAD改写为最终HEAD。

独立审计重算70份app分区且全部不变，复核422项产物哈希、214份fixture、70组前后帧、
286条声明检查，并执行77次离线外设decoder。Nesso新case保留16个callback检查、11个marker步骤、
12个实际QMP输入。清场时及复核时owned guest均为0。

既有case的QMP/QOM记录并非全部结构化trace：24个QOM步骤无可选debug读回，4项QOM stdout另核。
保留argv/stdout/guest输出的既有证据边界，不声称每一步都有新的结构化trace。
这份native matrix不自动验证最终Device Service、原版应用用户流程、Pages或物理行为。
旧日期source summary的matrix NOT RUN不改写；新增独立bounded receipt明确记录后续PASS。

## 原版应用非回归 follow-up

| 同原版固件实际路径 | 时长 | 控制 | 应用结论 |
| --- | --- | --- | --- |
| Mesh A：30 秒长按 1.2 秒、40 秒默认短按 | 150 秒 | PASS 8/8 | 单独视觉 PASS：Welcome→Back→US；原 raw REVIEW 保留 |
| Bruce：触摸、重置、重新挂载 | 150 秒 | PASS 6/6 | 单独视觉 PASS：Clock→reset WiFi；原 raw REVIEW 保留 |
| Honeypot：完整 153-byte USB 输出 | 180 秒 | PASS 7/7 | PARTIAL：AP 关联、HTTP 和 RF 未运行 |
| Mesh B：选择观察与自然睡眠/唤醒 | 150 秒 | FAIL 5/6 | before/after 选择画面不变；保留为失败负观察 |

最早 Mesh 轮次在10秒因固件实际从135×240旋转到240×135而被固定尺寸观察器拒绝；
清场端口检查还将 TIME_WAIT 误记为占用。两项均是私有观察器基础设施错误，
只修观察器后执行独立新轮次，没有修改产品、原固件、输入或150秒阈值。
初始报告的空检查与 raw application FAIL 不作为完整产品结论，也不覆写。

A 动作精确复用既有长/短合同，ZIP 证实虚拟保持时间1200/450ms、两次 A 输入、0 reset。
B 轮 ZIP 保留两次 B，A 成功不撤销 B 的原始 FAIL。自然睡眠黑屏单列，不能与选择响应混淆。
各完整轮运行中 ZIP 所有清单成员验哈希、原 app 分区前后不变；purge=0 后历史保留，
mutable Flash、lease、guest 与所属临时服务全部释放。具体固件/runtime/ROM/产物 SHA 见
`original-firmware-nonregression-summary.json` 与独立 A/B 审计。

实际执行源码仍为 `0e00cdcbc99a8210af6485df1bcfd04a514bc8a1`，523份相关 native 实现
与最终 main `70ef503fc2fb8b2c787fa9065e2952f525c40099` 字节一致；最终服务源码另有更新，
不能把这一源码关系写成在最终服务执行。常驻后验、Pages、外部归档由独立记录覆盖。

## 最终主分支功能复验

修复已合入 `70ef503fc2fb8b2c787fa9065e2952f525c40099`。同提交 main CI
[43496500912](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43496500912)
的 `platform-contracts` 与 `network-namespace-policy` 均通过；CI 的 PR scope 步骤跳过，
不能替代已有的本地 scope 检查。先前 suite、矩阵与应用运行保持各自真实执行源码。

最终源码再次通过普通 Device Service 运行同一份 `16255a35…` VFS 合成固件。USB 日志有
两次 GPIO3 READY、两次完整 DONE，每轮16项、六次 callback。22次实际输入严格分为两组，
中间恰好一次 reset；禁用/保持负控、按钮和触摸共享低电平、最后一源释放全部通过。
取证时同一 guest 仍运行，ZIP 的八个成员逐一复算，原 app 分区保持 `4743d8b5…`，
实际结果帧为135×240绿色 PASS。取证后 guest、Flash、lease 均释放，历史保留。

独立审计把最终5,664个源码文件逐个核对 SHA256 与 Git blob，并重新核对 native/ROM/站点
固定资产；三份独立或视觉复核引用的原始摘要哈希均附于功能摘要。此前测试包装器在
执行 helper 前因输入字段形状判断失败，服务调用和guest创建均为0；该FAIL单独保留，
不得算作原固件功能失败或被后续PASS覆盖。本地部署备份、启动器与实例细节不纳入公开功能记录。
