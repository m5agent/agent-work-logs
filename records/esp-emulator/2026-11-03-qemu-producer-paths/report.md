# QEMU producer 公开路径修复报告

## 背景与根因

发布前的旧本地 WASM 审计发现实际构建机路径。旧产物的 164 处命中中，162 处来自源位置宏，另 2 处来自配置的安装路径；本记录只公开类别、计数和产物哈希，不公开实际前缀字符串。该旧本地产物已撤回，先前 guest 验证作为历史保留，不能为本次新二进制授予 PASS。

仅做文本替换会修改已构建的 executable，而且无法闭合来源。因此在 producer 修复：编译器 `-ffile-prefix-map` 映射 project/cache/SDK/reused-dependency 的源位置；GLib 使用逻辑 `/usr` 和 `lib`，通过 owned `DESTDIR` 安装，库和头文件原字节复制到 host target，仅 `.pc` prefix 供 host dependency lookup 重定位；依赖回执记录版本化路径策略，旧缓存拒绝复用；编译输出、源码包成员和 runtime manifest 分发前 fail closed 扫描。

断言表达式和行为保留，不用禁用断言或增大栈改变客体时序。QEMU C 补丁、72 项顺序 source lock、160 postimages、板模型和 CPU 时钟均未改变；改变的是 producer 配方和由其产生的新 runtime。GLib 路径配置字节确实变化，不能据源代码未变就继承旧 guest 结果。

## 改动与兼容范围

base `189dc01a5ee42a23ac7e246f8390c2acfe471ffa` → target `1b86ed6f7edcc36deafc4834b45a28c6a6017c79` 只含 4 文件：

- `scripts/qemu-wasm-build/build.py`：编译前缀、GLib staged 安装、缓存策略与产物扫描。
- `scripts/qemu-wasm-build/README.md`：构建和验证边界。
- `platform/tests/test_bootstrap_qemu_browser_runtime.py`：路径正负控、真实 native C/C++、staging/pkg-config 和 producer 调用控制。
- `docs/project-snapshot.md`：生成快照。

补丁在一次性临时目录从 base 原 blob 正向检查、实际应用、逐文件与 target 比对，并反向检查。没有修改原 worktree/index/ref；细节见[补丁应用摘要](evidence/repair-patch-summary.json)。

## Fresh 构建与独立审计

固定 SDK 为 Emscripten `3.1.50` / emsdk `e2627e265d940db5ea58dffa63e490375bfc92e5`。recipe SHA-256 为 `f69cd135c8d5bb6c1efe920eb2ec54070798267b304c1333b9397fbde18770fc`，lock SHA-256 为 `b9b137e52e77078cc67cb5b25433622f62d70cc3cbed8f92ee6699eed3389a1b`。8 个依赖库没有复用旧对象；QEMU fresh Ninja `1446/1446` 完成。最终链接 O3，stack/default pthread stack 均为 64 KiB，stack overflow check 为 2。

新 runtime manifest SHA-256 `897114f09d5e0c695e44e665611fec4fa98aa62856cddce6eb1cbb906d21071c`；WASM `3c6b249002d83118e0ddcbd82e4ee6336223293b98566fc7709d5087d9df4567`，`12745460` bytes；对应源码包 `3bf6ee4fe907aff960ace53ae4622356345960055e0cb1cc1dee964ff6fc09b0`，`35241880` bytes。六文件实际字节和 source/recipe/lock 身份由[独立摘要](evidence/runtime-independent-summary.json)闭合。源码包实际成员已解压审计，不能用压缩文件的零命中代替成员扫描。

14 个实际 WASM section 中 producer 路径命中为零。完整导出的 2127 个资产也完成已知 prefix 检查；glue 的两个通用 Emscripten 虚拟文件系统 HOME 字面量经过明确分类保留，并非构建机路径。源码中通用文档示例路径与实际 producer 路径分开，不声称任何一般路径字符串都被删除。

新站点 manifest 为 `c5991d737d4b20c4b1ae96b71587cec907a1e72f3c57fe2fee63c08e23daf323`，根路径 `/m5stack-esp-emulator/`，publication_eligible 元数据为 true；该字段只是出口契约，不代表 full gate 或实际发布已完成。

## Cardputer-ADV 同实现路径验证

使用本次导出资源和实际新 WASM，reference full-flash SHA-256 `9ca3d53adf8bc81013a1062461961c27ae0450c1ee5e5b1ece6c21753818623b`，profile `cardputer-adv-wasm-wallclock`、clock divisor `1`、`oneInsnPerTb=false`。固件和 ROM 只在本地虚拟执行读取，不复制到本归档。

原始报告 SHA-256 `7f9f5f7fc53eebcf4a1fea63f38f673f67cbdbc6a652ede6c2c579951e30192f`，`101255` bytes，69 项检查均通过。实际串口 ready 说明 controller 为 TCA8418、receive mode 为 `official-driver-fifo-poll`。11 个真实 DOM 键映射到 controller/原固件 FIFO，按下、count 和释放各 11 个；count 从 1 连续到 11，22 个成功 controller 输入回执与原 session 的输入历史一致。未知按钮正向拒绝，没有伪造 controller 值。

同 session/fw/runtime 的前后帧 SHA 已从 RGB565 pixels 独立重算，前帧 `7e3cb9a173bda3d4260f39a067aa8067d3179f9eaecdec7840ac53a211b04b6e`，后帧 `57562843fad92927cdf520e8e58638332bcf942c9a15ca7e39047827748cd75c`。帧为 240×135，32400 个 native pixel 与 render 后模型 texture 全量匹配；portrait/landscape 表现收敛属于已观测的软件呈现结果，不是光学或物理显示证据。

串口包含 1 条启动时 I2C 未初始化提示，摘要保留此边界；随后 ready、输入和显示路径正常。声明的 panic/watchdog/Python traceback/Double marker 未出现。暂停冻结 guest、恢复后新 heartbeat，最后真实 QMP quit 导致 exit code 0。owner normal termination 为 1、fallback 为 0；iframe 删除前后独立 CDP 图中 6 targets 均 destroyed 且 live=0，不只依赖 owner 的通知计数。

[Cardputer-ADV 摘要](evidence/cardputer-adv-validation-summary.json)保留原报告/快照/PNG 哈希、session/target SHA、串口类型、键位/计数、实际 frame 和 closure。它没有复制原始身份、endpoint、pixels 或 Flash。

## 分层结果

| 层级 | 状态 | 范围 |
| --- | --- | --- |
| producer/host contracts | PASS | 17 bootstrap、10 exporter；host 控制不替代 guest |
| fresh build | PASS | 新配方、8 库和全部 QEMU；最终产物重新验哈希 |
| executable/source privacy | PASS | 声明的实际 producer 前缀、14 section、源码包成员、2127 资产及公开虚拟 HOME 分类 |
| transport / device_response | PASS | 本次 Cardputer-ADV 原驱动 FIFO 键事件及串口 |
| data_behavior / virtual visual | PASS | 同 guest 的 count、状态像素、native frame→render texture |
| runtime cleanup | PASS | 本例 exit0、无 fallback、6 个真实 targets 全关闭 |
| 完整 20 例 | PARTIAL | 编写本记录时 RUNNING；不授 aggregate PASS |
| Pages/线上 guest | NOT RUN | prepared preview 尚未发布 |
| physical hardware / 长稳 | NOT RUN | 没有运行 |

## 复现与证据边界

在公开 source commit 的干净 checkout 中，使用全新的 output/cache，固定的 SDK，禁止复用旧 policy 依赖：

```bash
python3 platform/tools/bootstrap_qemu_browser_runtime.py \
  --cache "$BUILD_CACHE" --output "$RUNTIME_OUTPUT" \
  --sdk-dir "$PINNED_SDK" --jobs 2
python3 platform/tools/build_public_site.py \
  --output "$SITE_OUTPUT" --base-path /m5stack-esp-emulator/ \
  --qemu-runtime "$RUNTIME_OUTPUT" --littlefs-runtime "$LITTLEFS_RUNTIME"
M5_PUBLIC_SITE="$SITE_OUTPUT" M5_PUBLIC_BASE_PATH=/m5stack-esp-emulator/ \
M5_PUBLIC_UI=1 M5_QEMU_DEVICE=cardputer-adv M5_PUBLIC_QEMU_OUT="$CARDPUTER_EVIDENCE" \
M5_WASM_CHROME="$CHROME_EXECUTABLE" M5_WASM_GPU=hardware \
node platform/tests/test_public_qemu_board_guest.mjs
```

变量由执行者设置到新 owned 目录；ROM/reference 输入沿仓库定义的下载/SHA 校验路径取得，不需要包含于源码或报告。上述命令描述对应的构建与公开板例路径；host tests、artifact 审计和实际 guest 结果各自独立。

正式 CI [41617152984](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41617152984)在 e950 CoreS3 案例保留 engine Worker target 的失败仍未定根因，deployment skipped。不得把本例成功描述为该问题已修复，也不能把本地新 runtime 与失败的 CI runtime 当同一产物。Factory 已知 gap、任意 firmware、其它设备提速、长时间运行和物理属性不在本记录的 PASS 中。

## 风险与回滚

新 producer policy 会拒绝旧依赖缓存，是预期行为；需要新构建目录。若回退 source commit，应保留本次完整 receipts/失败记录，对明确的旧源码重新构建和验收，不重写 main 历史，不替换某个 manifest 来混合两版 executable。旧包含真实私有路径的本地产物不应重新分发。这个子记录尚未发布 preview，也没有授权任意复制 ROM/固件或可变 Flash。
