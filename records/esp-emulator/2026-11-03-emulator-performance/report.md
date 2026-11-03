# ESP Emulator 性能修复报告

## 背景

- 来源：用户对同设备、同固件在本项目与[参照站点](https://zhuzhe1983.github.io/esp-online-tester/platform/)的启动时间与运行实时性提出疑问，并授权修复及对照验证。
- 现象：旧 browser 路径启动慢，显示和舵机动作稀疏；本地 native 服务的显示交付也有额外串行等待。
- 目标：保持 QEMU 的 SoC/controller/固件真实执行路径，缩短准备和启动、改善帧/输出交付，同时保留未知固件默认行为和会话清理。

## 结论

整体 `PARTIAL`，精确样本和固定 fixture 的性能/功能检查 `PASS`。不能把原因归结为“外设多所以包更大”。下载、校验、WASM 编译/实例化、TCI/helper、GPIO/MMIO、TB 边界及浏览器交付都参与成本。旧 dance 产品使用 div6，新准入 full SHA 使用正常 clock1 和现有 one-insn TB；前后比较包含产品配置改变，不是固定时钟的纯 CPU 实验。

最终仍用单一 QEMU TCI。实验 JIT 同样使用 QEMU SoC，但引入约6千行 host backend、64位 TCG 寄存器/另一个 cold interpreter 与直接 TLB 路径；关闭 JIT 也不能还原产品32位 TCI。真实 Factory 对照确认它执行了编译代码，仍有 WDT/Double，故未并入。Factory 的完整根因仍未定位；不得说禁日志、oneInsn 或 JIT 已修好该固件。

## 改动范围、兼容性和影响

启动采用一次文件读取、WebCrypto SHA、并行加载、经过 SHA 校验的有界 immutable asset cache 与编译模块复用；每次仍创建新 guest memory/Flash/eFuse/Worker。最终源构建对 C 对象使用 O2、最终 Emscripten 链接使用经实际 argv 审计的 O3。typed helper 只覆盖审查过的签名，其余走原 libffi。GPIO 事务避免多余解析/时钟采样，同时保留 raw 保留位、revision/IRQ/回调顺序及旧 API 回落；曾发现 reset-listener 后 stale IRQ，已修并保留真实负控。

CSTACK 只在明确 startup opt-in 时准备诊断；默认不做日志 ID/SP/heap 查询。正常 WDT、异常与真实 guest 时钟没有被关闭。单指令 TB 只在完整固件 SHA、正常 clock1 与所需 `0027` patch 身份同时匹配时使用；host/engine 双侧检查，不能把新 registry 混配旧 runtime。CoreS3 默认未知固件仍 div8，既有 e950 SDK 候选行与原始 main.py 的789612参考行分开。

browser frame、QMP 输出和方向各自有界、单请求在途；native frame/SCS 与 metadata/serial 解耦并维持 owner/generation/stop 栅栏。自动模式优先兼容的已连接 native，显式 browser 保持 browser lane。方向更新仅对当前拥有者，用已保留真实 `lastFrame` 同一 pixels/sequence 重绘，不制造 guest frame 或控制器值。

## 构建与来源

base `3691870c27b028dde76202e42ecddba31d1547c1`；R6 被测 source `8dd39cac835f6325a3f0aa815ca0d8471b025e6b`；最终交付 source commit：`69b26f3b72e7a3246048d58f6b77d649155790a7`。

QEMU base `40edccac415693c5130f91c01d84176ae6008566`，Emscripten3.1.50。完整 fresh 构建为72层 patch、160个源码 postimage、8个库和全部目标对象重建，独立副本正逆重放72层并验证原构建未变。main/default pthread stack64KiB、overflow guard2；这不证明所有深栈路径安全。

| 最终 artifact | SHA-256 |
| --- | --- |
| WASM | `0bd9478743d640484cad4762b9d7f7ae57a222f83ebf12a2114eb764a05194ea` |
| runtime manifest | `c441473d53dbdd47450c14ae5eafbc04f995f8a210eebdc0447b38a5d844bd9c` |
| corresponding source archive | `8faf5ec50cc3f5709bc0f1311f221ede8a180eb11ecd1fb9218c367cbbb09ecf` |
| R6 site manifest | `d716a3de85713baf46acae91113781895817c9377d48578ee70a9dd0a4f068ff` |
| required GPIO patch | `43685da86d9b959b2e769cd9cda5785a5c4039b5076f73f3b9d6033d1d161bdf` |

其余JS/Worker/NOTICE/锁/recipe/库和编译命令身份见 [build](evidence/build-r4-summary.json)。记录不分发 firmware/ROM/WASM 二进制；运行时发行须保留实际对应源码和许可。

## 实际执行和证据

### 最终 R6 StackChan

完整 Flash SHA `c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542`，匹配 source `7ee22ca570acd7f105d8205b3bc67ecc19e60ce11b1533f3481fc1288081bb9e`。实际 Metal 模型画布，冷/同页 warm 各约20秒；实际参数为单一 `tcg,thread=multi,one-insn-per-tb=on`，无 icount/CPU 覆盖。

| R6 观测 | cold | same-page warm |
| --- | ---: | ---: |
| Run 到真实 ready marker / s | 3.558965 | 2.745960 |
| 首非黑 frame / s | 3.571830 | 2.779860 |
| 实际 packet 增量 | 168 | 166 |
| 同 lane 实际位置变化 | 165 | 163 |
| 串口 dance cue | 30 | 30 |
| 像素变化更新 / s | 26.20 | 26.45 |
| 真实 render 角度变化 | 712 | 701 |
| 中间 pose | 637 | 632 |
| window 最大 frame 间隔 / ms | 1297.095 | 1265.435 |
| window 最大 controller 观测间隔 / ms | 2903.650 | 2895.695 |
| window 最大 render 观测间隔 / ms | 1262.380 | 70.745 |

全部间隔保留，不能据 warm 的70.745ms写“暖运行没有早期长间隔”。[间隔上下文](evidence/startup-gap-summary.json)把源程序1250ms bootcard 保持、1500ms首舞延迟、首次动作前 yaw0/pitch45/packets8不变及 viewer 按需 render 机制分别列出。warm 完整 raw 也有约1262ms early render gap，其前端点比统计窗口早2.67ms而未计入窗口内最大值。截图发生在20秒采样后。此段 gap 不足以证明 RAF 冻结；未采 CPU profile，也不能绝对排除所有主线程阻塞。

[最终摘要](evidence/browser-final-stackchan-summary.json)保存真实帧尺寸、类型/模型布尔值、DOM known、原始单位、frame/controller gap 与 source/cache/cleanup 身份。未出现的显式 capability 字段标 NOTCAPTURED。独立 [审计](evidence/stackchan-final-independent-summary.json)从398次原始位置和固定 mapping 重算 target，并验证 QOM→DOM→实际 render、session/firmware 绑定。全部正常exit0、无 fallback、观察到的 Worker 全部退出，无 panic/WDT/reset。它不证明物理舵机角度或机械速度。

独立8秒触摸执行：可信 pointer hold509.03ms，控制器 bits48→0，同 guest 在 down 后96.80ms出现 `DANCE restart in 650 ms`，post-ready窗口10.50992s内结束，早于16s自动边界，输入前无同 marker。单次响应不等于通用延迟分位数，也不建立物理电容传感性能。

### 原始参考程序、StopWatch 与历史对照

[CoreS3 R5](evidence/browser-stock-compose-summary.json)是未改原始 main.py `767239…` 的完整789612参考镜像，clock1/oneInsn。ready13.150840/11.876465s；首非黑13.184790/11.904205s。site是b1d1…，不是R6d716…。新 Flash/session、compiled→memory、warm4个asset memory、两20秒窗口及12目标正常退出已验证。首个 raw5ffaa6…因测试仍期待旧div8而失败，不是 guest fault；真实失败清理保留。只修改3行测试期待，served来源和算法不变。早期候选“约13s可见UI上界”不替代这些准确串口 ready 数值。

[原 R4 数据](evidence/browser-r4-summary.json)中的同一789612/div8 ready27.576750/26.808405s保留，可作旧产品路径参考；clock/TB/profile/site/cache准备不同，不是纯 CPU 或归一化cache实验。历史同c854 baseline ready11.674s、参照站2.684s也有时钟/采样/缓存差别，不能用tick/degree的变化次数比值推导角速度。

R4 StopWatch 完整 `d231…1898` 源于原发布 BIN `639579…cbbe`、尾部仅补FF。首非黑5.654580/5.082850s；无可确认的应用 ready marker。真实A+B四receipt、guest导航串口及完整菜单四ROI共同证明界面，不把ACK或oncreate当完整UI。它的历史baseline15.735s、参照2.210s，仍有差距且不是R6新性能测量。

### 新固定例门禁与被弃旧门禁

[R6 gate](evidence/admitted-browser-summary.json)在同一最终site/runtime独立执行19板20例，552/552检查，包含cold/reopened stock原始程序和独立SDK候选。它不授予其他固件或整个产品全功能PASS。

[旧oracle](evidence/oracle-correction-summary.json)发现Playwright1.64.1把async predicate的Promise当truthy：两个实际值false曾被报告为PASS。旧PASS及中断5例不准入；新的显式Node awaited-evaluate loop只接受满足序号/时间/两个真实ROI hash的plain object。合成Canvas负控属于host-only，不是虚拟设备证据。

此前 Cardputer-ADV 的 gate 暴露呈现失败；独立 host replay 复现了 retained-frame 重绘缺口，但不把它认定为旧失败的唯一原因。修复后 [真实虚拟设备方向证明](evidence/orientation-repaint-summary.json)与新完整门禁分别取证；旧失败缺少fresh QOM和两阶段CDP的边界仍NOTCAPTURED，未事后补写。当前修复不改guest像素、sequence或输入。

### 保留 native 与 Factory 边界

原native r4四次、46/46限定检查及原 source/runtime pin保留。真实changed-PNG更新StackChan1.25→27.17/s、CoreS3 1.42→8.42/s；额外捕获也增加payload/CPU，不能当完整应用FPS。启动cache冷热不一致，所以不比较native启动速度。ZIP在purge0停止前取得、历史/末帧/PID清理均有证据。CoreS3实际callback成立；native Factory欢迎页两个20s无fault，但空隙坐标输入仅ACK，不能说完成导航。

[Native R6 proof](evidence/native-final-path-summary.json)只证明若干实际函数、output/calibration与served路径在允许差异下等价，不创建新guest/性能PASS；整个public.js/profile/registry已不同，历史pin不被替换成当前hash。

Factory vendor完整399108…仍有真实WDT/Double，root cause未定位。原始BIN411578…与尾补FF身份、native/browser差异保持记录；不能把固定StackChan probe的R6 gate套到这个vendor应用。实验JIT/TBcap/RR均不交付，见 [四lane诊断](evidence/jit-four-lane-summary.json) 与 [成本审查](evidence/jit-integration-cost-summary.json)。

## 验证结果

| 层级 | 状态 | 范围 |
| --- | --- | --- |
| build | PASS | 72 patch/160源码、8库/所有目标对象、6asset闭集，非guest推断 |
| transport | PASS | R6 serial/frame/QOM和原native路径，lane不混用 |
| device_response | PASS | 可信输入、真实控制器和同guest响应，限定相应固件 |
| data_behavior | PASS | 实际位置/DOM/target/真实pose；缺能力元数据不推导 |
| visual_or_physical | PARTIAL | 新pixel/input gate和方向重绘成立；物理行为/完整scanout/长稳未验证 |
| Factory vendor browser | FAIL | 已执行失败保留，未按普通重试覆盖 |
| final host QA | PASS | Python 3.12.14: 1942 tests, 10 skips, all remaining passed; Node contracts and required generated/source/diff checks passed.；[结果](evidence/host-production-checks-summary.json) |
| delivery | PASS | 本地审查分支、完整可应用补丁与本次归档；未合并/部署生产页面 |

## 可复现命令

在已检出的源码仓库内运行，变量由复现者提供；不在此写宿主私有路径或服务凭据。每个 output 必须是源码 ignored `.work/` 下的全新路径，重任务串行。外部reference/ROM按锁SHA取得，不复制到记录。

```sh
python3 platform/tools/bootstrap_qemu_browser_runtime.py \
  --cache "$QEMU_BUILD_DIR" --output "$QEMU_RUNTIME_DIR" \
  --downloads "$SOURCE_ARCHIVE_DIR" --jobs 2
python3 scripts/browser-littlefs/build.py \
  --emcc "$QEMU_BUILD_DIR/emsdk/upstream/emscripten/emcc" \
  --output "$LITTLEFS_RUNTIME_DIR"
npm ci --prefix platform/tests
python3 platform/tools/build_public_site.py --output "$SITE_DIR" \
  --base-path /perf/ --qemu-runtime "$QEMU_RUNTIME_DIR" \
  --littlefs-runtime "$LITTLEFS_RUNTIME_DIR"
M5_PUBLIC_SITE="$SITE_DIR" M5_PUBLIC_QEMU_OUT="$ADMITTED_OUT" \
  M5_PUBLIC_BASE_PATH=/perf/ M5_WASM_CHROME="$CHROME_EXECUTABLE" M5_WASM_GPU=hardware \
  node platform/tests/test_public_qemu_admitted_boards.mjs
M5_BENCH_ENGINE=qemu M5_BENCH_DEVICE=stackchan \
  M5_BENCH_SITE="$SITE_DIR" M5_WASM_CHROME="$CHROME_EXECUTABLE" \
  M5_BENCH_IMAGE="$DANCE_FULLFLASH" \
  M5_BENCH_IMAGE_SHA256=c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542 \
  M5_BENCH_RUNS=2 M5_BENCH_SAMPLE_MS=20000 M5_BENCH_REQUIRE_RENDERED_MOTION=1 \
  M5_BENCH_OUT="$DANCE_OUT" node platform/tests/benchmark_emulator_firmware.mjs
```

触摸单独使用同镜像、`M5_BENCH_RUNS=1`、`M5_BENCH_SAMPLE_MS=8000`、`M5_BENCH_INPUT=known-device-controls`及新output，再执行：

```sh
node platform/tests/derive_emulator_touch_response.mjs \
  "$TOUCH_OUT/report.json" "$TOUCH_OUT/response-validation.json" "$MATCHING_DANCE_SOURCE"
```

原始日志/执行harness/算法SHA/serial/frame/input/Worker lifecycle保留在各次输出；对外只复制已核验summary。native的公开重现入口为`node platform/tests/test_public_native_performance.mjs --execute`，需复现者提供独立服务所需环境，遵守证据ZIP-before-stop/history清理协议；不重用用户服务或将native结果拼成browser PASS。

## 风险、未覆盖项与回滚

任意固件、完整Factory应用、其他主机、长稳/多设备性能、RF/电气/声学/机械和真实物理时序未验证；未部署、未merge。固件/ROM发行许可不因公开URL而自动取得。正常虚拟Flash运行会变化，测试退出按各lane策略释放或保留；无物理不可逆写入。

回滚必须保持匹配的profile/helper/runtime/source manifest。撤销required0027时须同步撤销对应oneInsn变体，不能削弱校验混用旧runtime。JS展示交付可独立回退，但owner/stop栅栏不能删。历史失败、rawSHA和原native execution保留；早期仅 native 的归档记录保留在 Git 历史；本次追加 browser follow-up、最终代码检查与可应用补丁。

## 完整补丁复现

最终源码提交保存在本地 `m5agent/emulator-performance-20261103` 审查分支；
未推送源码分支或创建/合并 PR，也未部署。以下完整补丁包含该分支相对公开
base 的实现、测试、必要文档和有界证据。为避免包含无关历史文档的端点上下文，
使用零行上下文；必须显式使用 `--unidiff-zero`。新增代码中的 loopback 地址、
动态端口与 example.test 都是可复现单测 fixture，不是捕获的私有服务端点。

```sh
git clone https://github.com/m5agent/m5stack-esp-emulator.git
cd m5stack-esp-emulator
git checkout --detach 3691870c27b028dde76202e42ecddba31d1547c1
git apply --check --unidiff-zero "$PERFORMANCE_PATCH"
git apply --index --unidiff-zero "$PERFORMANCE_PATCH"
```

`PERFORMANCE_PATCH` 指向本记录的 [完整补丁](patches/0001-qemu-performance-repair.patch)。
独立 base checkout 已实际应用且所得 Git tree 与最终源码提交一致，见
[补丁验证](evidence/patch-apply-summary.json)。物理设备未操作，不存在硬件回滚。
