# ESP emulator 性能优化与 Pages 交付报告

## 背景与当前范围

用户要求把性能优化合 main，并更新 GitHub Pages。本记录按源码合并、构建与隐私、完整功能 gate、部署和线上 actual guest 分层；当前总体 **PARTIAL**：完整本地功能门禁、prepared-preview 部署及 48 路实际 HTTPS bytes 回读已通过；线上四阶段前三通过，但独立触摸轮首次启动失败，输入和响应推导 NOT RUN；没有把静态资源、部署控制面或 cleanup 当作完整线上功能 PASS。

历史固定证据分别是[性能调查报告](https://github.com/m5agent/agent-work-logs/blob/73cf198d7d3808e9f66e9cce8faa1349f9a0a9e4/records/esp-emulator/2026-11-03-emulator-performance/report.md)和[producer 公开路径修复子记录](https://github.com/m5agent/agent-work-logs/blob/2c4f5fcf9469ac8f6935a29359489003705cc76e/records/esp-emulator/2026-11-03-qemu-producer-paths/report.md)。它们可以支撑自己的既有结果，不能替代本次新 runtime 或线上执行。

## 合并与 CI 时间线

1. PR163 的原性能 head `69b26f3b72e7a3246048d58f6b77d649155790a7` 首次 CI 的三项失败来自 glibc 断言 stderr 中两个真实测试程序的 argv[0] 不同。测试框架固定诊断身份，同时保留真实 `executable=`、断言表达式、函数名、signal/stdout/stderr 差异比较；产品路径没有为测试而修改。首失败日志和成功日志独立保留。
2. 最终 PR163 head `d1d31db717fd62a5dae666131600f17ea218fbab` 的两次 CI 触发共四检查通过，平台实际 1943 tests、10 skipped。PR163 合入 `189dc01a5ee42a23ac7e246f8390c2acfe471ffa`，merge/head tree 同为 `bfb7179432afab97ef296ed61e996d77f7cbf970`；main CI `41617122831` 的 platform-contracts、network-namespace-policy 均通过。
3. 正式 Pages run [41617152984](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41617152984)的源码构建、ABI 和 synthetic Canvas 控制通过，但 gate 第三个 e950 CoreS3 案例停止后 engine target 未在门禁内消失。5 个 pthread targets 已关闭、guest exit0、owner normal1/fallback0，只能证明各自这些步骤；残留 engine target 仍使门禁 **FAIL**。直到 context teardown 的关闭不能反填为正常 cleanup。部署 **SKIPPED**，旧线上站点未因此改变；根因仍未定位。
4. 发布前另发现旧本地 WASM 的 producer 私有路径：164 处中 162 为源位置宏，2 为配置安装路径。该旧 runtime 和其部分四例结果撤回发布准入。记录仅保留类别/计数/哈希，不公开实际路径；不通过修改成品 WASM 来掩盖。
5. PR164 把路径修复放在 producer：编译器 source-prefix map、GLib 逻辑 `/usr` staged 安装、只重定位 host `.pc` prefix、版本化依赖缓存策略和分发扫描。它没有修改 QEMU C 补丁、source lock、时钟或断言策略。PR164 head `1b86ed6f7edcc36deafc4834b45a28c6a6017c79` 的 push `41625517780`、pull_request `41626388927` 各两检查通过；`2026-11-03T11:24:12Z` 合入 main `10788607feefb9e532c2dd1fe4679adcd6aa0fc2`。两者 tree 均为 `9158da43530d82d0eaf5472eff15f831e82666e8`。随后 main107 的 CI `41627233963` 也成功，实际平台 1949 tests、10 skipped、152.154 秒；见[独立 CI 摘要](evidence/producer-main-ci-summary.json)。

6. 文档与证据收口提交 `b41eba70eb61f7ddc5c41e0b981341064f9d1d1f` 已推送并快进本地 main；相对 main107 的 17 项变更全部在 `docs/`，所有非 docs 字节保持不变。22 个 product web、build recipe 和 source lock 不变；没有因该文档提交重部署站点。当前完整 tree 为 `3ad85b0202f959d500157b6c0113d3006dccf809`，与 producer/main107 的 `9158da43530d82d0eaf5472eff15f831e82666e8` **不同**；只有产品闭包按字节等价，不能把整个 b41 tree 写成等于 1b。

本地 50 个 docs tests（12.360s）与 runtime-coverage、peripheral-catalog、qemu-profiles、project-snapshot 四生成器检查通过；scope 检查 17 new blobs、1,032,656 bytes，新增 evidence 192,880 bytes，无错误。见[文档交付摘要](evidence/docs-source-delivery-summary.json)。新 main CI [41631441210](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41631441210)已 **PASS**：platform-contracts 与 network-namespace-policy 均成功，1949 tests、10 skipped、151.535 秒；[终态摘要](evidence/current-main-ci-summary.json)保留实际日志哈希。

本地 main 已快进且干净，既有可恢复编辑完整保留。本公开记录没有备份位置、stash 标识或运行环境私有细节。

## 新 producer 构建与已部署出口

新 build/出口的源码是 PR164 head，与合并 main Git tree 相同，但构建身份和部署身份仍独立记录。固定 Emscripten `3.1.50` / emsdk `e2627e265d940db5ea58dffa63e490375bfc92e5`；8 个库与 QEMU 全 fresh，Ninja `1446/1446` 完成，没有复用旧依赖。72 patches 和 160 postimages 的 source lock 未改变。

| 项目 | 本次已核实际身份 |
| --- | --- |
| recipe SHA-256 | `f69cd135c8d5bb6c1efe920eb2ec54070798267b304c1333b9397fbde18770fc` |
| source lock SHA-256 | `b9b137e52e77078cc67cb5b25433622f62d70cc3cbed8f92ee6699eed3389a1b` |
| runtime manifest SHA-256 | `897114f09d5e0c695e44e665611fec4fa98aa62856cddce6eb1cbb906d21071c` |
| WASM SHA-256 / bytes | `3c6b249002d83118e0ddcbd82e4ee6336223293b98566fc7709d5087d9df4567` / `12745460` |
| 对应源码包 SHA-256 / bytes | `3bf6ee4fe907aff960ace53ae4622356345960055e0cb1cc1dee964ff6fc09b0` / `35241880` |
| 准备站点 manifest SHA-256 | `c5991d737d4b20c4b1ae96b71587cec907a1e72f3c57fe2fee63c08e23daf323` |
| 导出根路径 / 资产数 | `/m5stack-esp-emulator/` / `2127` |

14 个实际 WASM section、六个 runtime 文件、解压源码成员、8 个依赖及全部导出资产完成声明范围的 privacy 审计。GLib 公开逻辑安装路径和两个通用 Emscripten 虚拟 HOME 字面量与实际构建机路径分开分类，没有把上游文档示例字符串误当机密，也不把压缩文件扫描代替成员扫描。

出口 `publication_eligible=true` 仅是元数据契约。当前包已经过完整门禁并成功 prepared-preview 部署，实际 HTTPS 列明路径也已逐字回读；线上 guest 仍须独立完成，不能据静态资源或 deploy job 单独授予线上功能 PASS。详细、已固定的 build/source/privacy/Cardputer-ADV 证明见 producer 子记录。

## 新完整 gate 与部署状态

完整新 gate 使用上述 exact WASM/site，按公开路由逐板独立执行，已 **20/20、19 板型、552/552 PASS**。实际执行从 `2026-11-03T11:09:31.166Z` 至 `2026-11-03T11:34:07.853Z`；22 个 VM 累计 102 个 pthread、22 个 engine normal termination、0 fallback，共 124 个 distinct observed targets，final live=0。wrapper 报告 SHA-256 `8281af8207f2b036eb33f0269e28adc880a5a650d7968e592c974c1a47617d95`，审核后[功能摘要](evidence/full-browser-gate-summary.json) SHA-256 `947ae11865a4659e7bd6453ba2ba7e6e130f5f766501a9139efca484d625f054`。19 板型/20 用例是功能覆盖范围，不等价于每个设备都提速。

已完成的 Cardputer-ADV 子例 69/69 通过，实际 11 键原驱动 FIFO 输入、同 guest 像素/texture、pause/resume、exit0，以及 6 个 actual CDP targets 关闭均绑定新 runtime。该单例不单独授予其它板型结论；其它公开参考例由完整 gate 分别取证，Factory 固件与正式 CI e950 cleanup 问题仍独立保留。

最终使用 existing prepared-preview 应急 workflow `public-site-prepared-preview.yml`，上传已冻结的完整静态出口，不由该 workflow 重建 C/QEMU。完整包为 `public-site-preview-live.tar.gz`，`146747803` bytes，SHA-256 `d4be918692aa7d63cdf6f6360da2cfc2c3337b2f07ad96fce011f1d3bfe2fe4a`；2128 个 regular members 对应 2127 个 manifest 资产及 manifest 自身，逐文件 size/SHA、路径/owner/time 与源码闭包见[包摘要](evidence/prepared-package-summary.json)和[独立审计](evidence/prepared-tar-independent-summary.json)。

Release tag `pages-performance-20261103-10788607` 指向 main107，发布于 `2026-11-03T11:36:57Z`，tar、validation summary、package summary 三项上传 asset 全部下载回读一致，见[传输摘要](evidence/release-readback-summary.json)。prepared-preview run [41629045946](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41629045946) 的 prepare/deploy 均 success，状态更新 `2026-11-03T11:38:17Z`。Pages artifact `13226524508` 的平台包装 digest 为 `sha256:94279190a0431edeb0d7eec5a091f0b0169414fa8bd2d5d3e9a599a48281708d`，与 release tar 是不同包装角色，不混用哈希。

该路径不同于失败的正式 `public-site.yml`，不能描述为正式 CI 生产流程通过。[部署控制面摘要](evidence/prepared-deployment-summary.json)与下述真实 HTTPS 回读分别取证，二者都不替代 actual firmware 执行。

实际 HTTPS 回读从 `2026-11-03T11:38:49.776Z` 至 `2026-11-03T11:39:14.253Z`，共 48 GET、49,173,223 bytes，全部 200、无重定向，实际 bytes 与冻结出口一致。范围为 manifest、6 个 QEMU runtime 文件、22 个执行 web 路径、13 个 LittleFS 文件及 6 个入口/隔离/配置路径；不是对线上全部 2127 个资产的下载声明。独立 canonical manifest 回读也为 429386 bytes、SHA `c5991d737d4b20c4b1ae96b71587cec907a1e72f3c57fe2fee63c08e23daf323`。见[HTTP 摘要](evidence/live-https-assets-summary.json)和[canonical 回读](evidence/canonical-online-manifest-summary.json)。

实际 HTTP 源码包 SHA `3bf6ee4fe907aff960ace53ae4622356345960055e0cb1cc1dee964ff6fc09b0` 与已独立审计的源码包字节相同，因此只复用对应的 source postimage/patch/recipe/lock 语义审计；本次 HTTP 检查没有重新构建或重新解压审计源码包。

## 实际 HTTPS guest：三阶段通过，一阶段首启动失败

四阶段均绑定上述同一 HTTPS site/runtime/WASM/source lock；证据不从本地或 native 路径继承。

| 阶段 | 功能结果 | 范围与执行身份 | 独立清理 |
| --- | --- | --- | --- |
| 1 CoreS3 原始 stock | PASS，49 检查 | full Flash `78961297e751ec9c743b4cdf89cc2c137e7e2c801dda3ead9df2ea45d59fbd3f`；tracked `test_public_qemu_guest.mjs`，实际 SHA `60dd91681b8cc85b10468becd028faa2a1702e180590ab23344613429372dbe9`；650ms 手势，真实单帧双 ROI；启动时长未测 | 两 VM、12 targets 全关闭 |
| 2 StackChan 默认 reference | PASS，24 检查 | full Flash `407f6260400da1b0d10d2374917c7eabd43e6b3bed614afcb97a8d09a7f4af18`；原 adapter board runner；startup 时长未测 | 一 VM、6 targets 全关闭 |
| 3 同 c854 dance，两轮 20s | PASS（限定采样窗） | 原 benchmark adapter；normal clock1、one-insn 绑定 patch43685；实际 QOM→DOM→render trace | 两 VM、最终累计 12 targets 全关闭 |
| 4 同 c854 独立 8s touch | **FAIL：ready 前启动异常** | 120s 未 ready；0 frame、0 input；touch + response derive **NOT RUN** | 一 VM仍 exit0、6 targets 全关闭 |

阶段 1 的 suite preflight 记录原 adapter identity，但实际执行的是固定源码里的 tracked CoreS3 runner；不能称它由 ignored board adapter 执行。阶段 2–4 的原 adapter identity 都为 `ecc887184178b99656bdada419502355940ee6cec7ec45a405c2259a822efa87`，其 15 个冻结成员可通过 [code/README.md](code/README.md) 的 seed 包逐字恢复。source restoration 没有冒充新的 online execution。

阶段 3 两轮 ready 分别为 **5.320070 / 3.982515 秒**，像素变化观测约 **26.696 / 26.348 次/秒**；这是实际 callback/pixel 观察，不是完整物理显示 FPS。对应 packet delta 为 169/166，位置变化观察 163/161，30/30 cue，实际 rendered angle 变化 697/682、中间 pose 624/613；逐项见[舞蹈摘要](evidence/online-dance-summary.json)。

最大间隔如实保留：两轮 frame gap 1280.175/1263.805ms，state gap 2855.275/2845.930ms，render gap 1245.640/1244.510ms。匹配源码有 1250ms boot-card 保持与 1500ms 初始 cue 延迟，但本次没有独立建立每个最大 gap 的因果归属，不删除这些数值或保证所有时刻实时。首次是 fresh browser/guest/module，不是 cold network；artifact preflight 已暖 CDN，不能与本地 R6 网络条件作单因素时间比较。

阶段 4 的首次真实失败原报告 SHA `5975563a8689fc427ccaede5c9a18a2d695fab6118470b9edcbaff6894918650` 保留。应用 ready 前 CPU1 `LoadStorePIFAddrError`，ROM PC `0x40001c38`、EXCCAUSE `0x0000000f`、EXCVADDR `0x40001c34`；观察到 2 个 runtime RESET events。串口只显示一次 reboot，事件条数不能直接当独立 reboot 次数。120000ms 等待结束仍处于 booting，没有 frame 或 input，因此独立触摸和响应推导没有运行。根因未建立，没有修改 firmware、clock、WDT，也没有普通重试覆盖此首失败。

全部阶段共 6 个 VM、36 个实际 Worker targets 关闭，normal exit code0、owner fallback0；这证明清理，不证明失败 VM 的应用功能。前两轮 c854 dance 通过不证明每次启动稳定，reference 固件输入通过不证明 c854 的独立触摸协议通过；历史 R6 touch 必须留在其旧 runtime 身份下。

[四阶段总审计](evidence/online-four-stage-summary.json)进一步绑定所有执行 web/source、实际 runner/adapter 身份和累计 target 计数；原始功能失败不被清理通过抵消。四份原样安全摘要：[CoreS3](evidence/online-cores3-stock-summary.json)、[reference](evidence/online-stackchan-reference-summary.json)、[dance](evidence/online-dance-summary.json)、[首次 touch startup failure](evidence/online-touch-startup-failure-summary.json)。当前总体 **PARTIAL**，不是完整 online PASS。

## 分层验证

| 层级 | 状态 | 范围 |
| --- | --- | --- |
| source delivery | PASS | PR163、PR164 合 main，final head/main tree 分别吻合 |
| host CI（产品交付） | PASS | 两个 PR 各四检查；main189/main107 各两检查；main107 平台1949/10skip |
| docs-only b41 本地验证/推送 | PASS | 50 docs tests、四生成器、scope；17变更全docs，未重部署 |
| docs-only b41 main CI | PASS | `41631441210` platform/network 通过；1949 tests、10 skipped |
| fresh build/privacy/source/export | PASS | 新 producer runtime 与对应源码/资产身份已独立审计 |
| 新 Cardputer-ADV 同路径 | PASS | 已固定的 scoped 69/69 虚拟设备证明 |
| 新完整 20 例 | PASS | 19板、20例、552检查；22VM、124 targets最终为零 |
| 旧正式 Pages gate | FAIL | e950 engine target cleanup；deployment SKIPPED |
| package/upload/prepared-preview 部署 | PASS | 包闭包、三项回读、prepare/deploy成功；独立于线上guest |
| 线上静态 transport/source bytes | PASS | 48 个列明 GET；不是全部 2127 个线上资产 |
| 线上 CoreS3/reference/dance | PASS | 三个阶段各自限定 firmware/采样窗通过 |
| 线上独立 c854 touch startup | FAIL | ready 前 ROM 异常；120s 未 ready、0帧/0输入 |
| 线上 touch input/response derive | NOT RUN | 启动失败，未进入输入窗口 |
| 线上 cleanup | PASS | 六 VM、36 actual targets最终零；不抵消功能失败 |
| hardware / 长时间稳定性 | NOT RUN | 未执行 |

## 复现入口

使用固定 source commit、全新 owned cache/output、固定 SDK 和可复建 LittleFS；不复用旧 producer-policy 依赖。下列环境变量由执行者设置，原始证据保留在 ignored 输出目录：

```bash
python3 platform/tools/bootstrap_qemu_browser_runtime.py \
  --cache "$BUILD_CACHE" --output "$RUNTIME_OUTPUT" \
  --sdk-dir "$PINNED_SDK" --jobs 2
python3 platform/tools/build_public_site.py \
  --output "$SITE_OUTPUT" --base-path /m5stack-esp-emulator/ \
  --qemu-runtime "$RUNTIME_OUTPUT" --littlefs-runtime "$LITTLEFS_RUNTIME"
M5_PUBLIC_SITE="$SITE_OUTPUT" M5_PUBLIC_BASE_PATH=/m5stack-esp-emulator/ \
M5_PUBLIC_QEMU_OUT="$FULL_GATE_OUTPUT" M5_WASM_CHROME="$CHROME_EXECUTABLE" \
M5_WASM_GPU=hardware node platform/tests/test_public_qemu_admitted_boards.mjs
```

上述 gate 仍要求 actual Worker targets 消失，不能用关闭整个 browser/context 替代；不延长超时来制造通过。本记录没有触发额外执行；实际 prepared-preview 发布使用上述固定 release tag 和 run。线上 adapter 的固定源码恢复与严格四 SHA 复现说明见[code/README.md](code/README.md)；线上阶段 2–4 的复现协议在该 code 说明中；阶段 1 使用 tracked CoreS3 runner。实际四阶段证据已逐项绑定，不把 source restoration 当 guest PASS。

## 边界与回滚

保留单一 QEMU/TCI，不集成第二 SoC 后端或实验 JIT。历史 native 路径和 browser 路径独立；ready、first frame、pixel 更新和模型 render 指标不混成物理 FPS。Factory gap、正式 CI engine cleanup 和本次独立触摸轮 ROM 启动异常根因、任意固件、长稳及物理/RF/功耗/机械属性均不被当前范围关闭。

源码回退使用新审核提交，不重写 main。部署回退必须用明确且隐私合格的完整 known-good 包并重新核 online/runtime 身份与 actual guest，不能只替换 manifest，不能重发已撤回的私有路径 runtime。失败正式 CI、旧隐私撤回、本次 build/gate/部署应保留为不同 execution，不覆盖历史。公开档案只放审核后的 summary、hash 和复现命令，不复制 raw logs、ROM/固件/Flash、私有 endpoint 或原 session/Worker 标识。

## 启动异常的只读定位

[独立四阶段审核](evidence/online-independent-review.json)重新核对实际原件、来源与 36 个 QEMU Worker 目标；线上整体保持 PARTIAL。
[ROM 定位](evidence/startup-rom-literal-diagnosis-summary.json)在 hash 匹配的 ROM/符号 ELF 上确认：PC `0x40001c38` 是 `__call__xtos_set_intlevel` 的 `l32r`，读取合法 ROM 字面量 `0x40001c34`（值 `0x400559cc`）。调用链位于 Core1 SysTick 中断与临界区退出路径。它不是已证实的任意 PSRAM 越界地址，也不足证明与旧事件同因或排除回归。

静态 IROM 覆盖该地址；当前异常把非 instruction 的失败 MemTx 汇总为 cause `0x0f`，但没有保存物理地址、MMU index、response 或命中 MemoryRegion。因而没有足够证据选定安全修复。后续最小诊断是首个失败事务的只读 trace，不增加 MMIO 读取、不改时钟或 WDT；本次未实施该 trace、修改 C、重建或普通重试。
