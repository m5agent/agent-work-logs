# ESP Emulator 性能修复与同固件对照报告

## 背景

用户要求解释并修复相同设备、相同固件在本模拟器中启动慢、运行不连续的问题。比较参照为公开的 ESP online tester；本记录只先归入能够独立支撑结论的 native r4 证据。浏览器中间原型与候选构建不在此初稿中充当最终结果。

## 结论

整体 `PARTIAL`。native 工作台取帧、实际 SCS 读回/DOM/模型渲染与自动路由通过限定虚拟设备验证。浏览器最终 r2 与既有准入设备回归待补，不声明最终提速、超过参照实现或全设备 PASS。

native 的 serial/status 与帧读取原先互相等待，帧端点的预览缓存也限制动画交付。修复为独立且单请求在途的帧、状态/串口与 SCS 输出循环，保持 ETag、会话/owner/generation、停止和取消栅栏。SCS 状态来自相同 guest 的固定 QOM 路径，验证固件和会话身份后才供给 DOM 和现有插值。自动模式在兼容服务已连接时优先 native，显式 browser 仍走独立浏览器路径。

浏览器的最终架构保留现有单一 QEMU TCI，优化 final-link O3、typed helper 与真实 GPIO 事务；精确完整固件 SHA 可选择正常时钟的 one-instruction TB，并严格绑定 required runtime patch。保留原控制器、DMA/FIFO、IRQ、固件字节和看门狗；保留经校验资源缓存、编译模块复用、并行加载和独立帧输出。JIT、第二 SoC 后端与 RR 试验已撤回，历史不抹去，也不继承到正式验收。

最终 GPIO patch 的回调后 IRQ 新鲜度还在单独复测和重建流程中；本初稿不冻结旧 patch SHA，不复制 candidate-r1 构建摘要。最终根因归因、性能数字和正式浏览器证据以 r2 为准。

## 已验证 native 结果

同一对内 native QEMU、固件字节和设备保持一致，主要对照取帧 controller；当前 public.js 另外连通真实输出到模型。每次稳态观察约 12 秒，单位为实际应用的变化 PNG 更新次数，包含 guest 分步绘图，不能解释为完成的应用帧或物理屏幕 FPS。

| 设备 | 更新/s 前 → 后 | PNG bytes 前 → 后 | 服务 CPU 前 → 后 |
| --- | ---: | ---: | ---: |
| StackChan | 1.25 → 27.17 | 30,974 → 590,587 | 0.92% → 13.63% |
| CoreS3 | 1.42 → 8.42 | 65,908 → 395,381 | 1.58% → 13.83% |

CPU 100% 对应一个逻辑主机核。更高编码/传输开销是更频繁取帧的实测成本，不描述为 native CPU 模拟器优化。启动速度未比较：第一侧 Flash 准备偏冷、第二侧缓存偏暖。

StackChan after 取得同 guest 的 70 次实际 QOM 输出观察，原始 yaw/pitch 分别有 47/32 个不同位置；真实 viewer render 回调采到 527 个 pose、366 个中间 pose。原始 DOM ticks、当前控制器位置与模型目标绑定一致，不用请求目标伪造输出。CoreS3 的真实控制器长按到达 guest 回调；StackChan touch 仅协议接受。

四次运行均在停止前取得证据 ZIP，校验内含文件哈希/大小，`purge=0` 后历史与最后帧仍可读，四个 native 运行进程全部退出。r1 harness 失败、r2 缺失 body bridge 诊断、r3 与 r4 的独立边界均保留在结构化证据中。

## 执行与复现

- 环境：native QEMU + 独立 Device Service + 真实公共工作台，Chromium 与 Apple M4 Metal 模型画布；软件 GPU fallback 被拒绝。
- 命令：`node platform/tests/test_public_native_performance.mjs --execute`。所需 artifact 环境变量名称列于 native JSON；不得写入路径、端点或凭据。使用隔离服务及新的不存在的输出目录，串行执行。
- native runtime SHA：`6d9af027e2f744208fc2503128f1772f436d7ca7358f9e53be597bc76800f39d`。
- native r4 原始报告 SHA：`63b0c51cd86066ccba707fef59ea9598425c84b51afcd807c494789409b66b35`。
- 固件、源文件、帧、保留帧、workbench、观察、历史和 ZIP 的完整哈希见 [native-summary.json](evidence/native-summary.json)。二进制和未经脱敏原始会话响应不在本记录中。
- 最终 browser r2 的精确命令、源码 commit、patch/runtime/firmware/config 与清理证据待补；不从 native 或原型结果推导。

## 验证结果

| 层级 | 状态 | 范围与依据 |
| --- | --- | --- |
| build | NOT RUN | 最终 r2 构建身份及证据尚未纳入；旧候选不替代 final |
| transport | PASS | native serial、实际变化帧、QOM 与证据 API，限定四次同 guest 运行 |
| device_response | PASS | native SCS 实际响应，CoreS3 控制器长按与 guest 回调 |
| data_behavior | PASS | native 原始位置、DOM、实际模型渲染与自动路由限定闭环 |
| visual_or_physical | PARTIAL | native 实际渲染动作通过；完整应用帧保真 REVIEW；物理行为未测 |
| browser_final_r2 | NOT RUN | 正式 runtime 的正常产品路径 guest 验收待补 |
| all_admitted_regression | NOT RUN | 既有浏览器准入设备回归待补 |
| delivery | NOT RUN | 未发布初稿；最终 source/record commit 和索引更新待补 |

## 验证边界

native 证据不是 browser-WASM CPU/runtime PASS。截图可以处在 guest 绘图中途，未执行完整应用帧像素 oracle。没有验证物理伺服速度、力矩、机械、电气、RF、光学、声学或内存时序。没有其他镜像、长稳、容量、其他主机与移动端结论。

正式 r2 必须保留实际 Module arguments、完整固件 SHA、runtime/source/patch 身份、应用串口、像素更新、真实输入与 SCS 进展、实际渲染 pose、栈界与 Worker 消失证据。位置变化次数只能在各自单位内统计，不能直接比较 QEMU ticks 与其他引擎 degrees。像素更新频率不等于物理 FPS。

## 风险与回滚

本任务没有物理设备写入或不可逆硬件操作。更频繁 PNG 捕获增加服务 CPU 和 payload；可恢复旧取帧 controller 来回退，必须保留本次证据。浏览器回退应同时恢复相应 profile/runtime 配对，不能削弱 patch 身份检查来混用新 registry 与旧 runtime。

该目录当前是本地初稿。未提交、未推送，也未改根索引。最终源码 commit、正式 r2 结果、既有准入设备回归及最终归档引用由根任务补齐后，再按仓库流程决定发布。
