# M5GFX #450 评审报告：board_spec 用 generate / verify 简化新增板卡

## 背景

- 条目：https://github.com/m5stack/M5GFX/pull/450 ，作者 ainyan03，2026-11-26 06:42Z 创建；
  评审前 OPEN、非 draft、0 评论 0 review，正文英文。
- head `a092ea5a85b047263e409448d6d33a7650b2141e`，base 为 `develop` tip
  `28b8a5c310075d6432a2096c7444dce5e5c7013f`（`Merge pull request #449`）。
- PR 动机：新增板卡需要分别跑多个生成器、三项检查，步骤分散在 catalog README、host test
  README 和测试里；失败只报“stale”，不告诉怎么修；并发板卡 PR 会在手维护的测试名单和
  重新生成的 editor bundle 上冲突。
- 评审范围：只读 diff、仓库自带 Node/C++ host 测试、`generate`/`verify` 行为对照、
  trial 板实验；不改上游、不 close、不 push。

## 改动范围

1. 贡献流程：README 新增 “Adding a board” 的三种选路（仅 `BOARD_ID`、已有 detector 变体、
   新 detector），新增 `npm run generate` / `npm run verify`；`check` 汇总列出所有缺失、
   过期、多余生成物并给出重生成命令；BoardSpec CI 增加 `src/lgfx/boards.hpp` 和
   `test/board_detect/generated/**` 触发路径，`check` 在 `npm test` 失败后仍执行；
   新增根级 PR 模板。
2. editor 可选化：删除跟踪的 `extras/board_spec/dist/board_spec_editor.html`
   （约 34k 行），`dist/` 加入 `.gitignore`，`check` 不再做 bundle 新鲜度比较，
   仍保留在内存中构建 bundle 的测试。
3. 去列表化：catalog 文件清单、unverified 名单、组合总数等全量列表改为“已有板卡固定期望 +
   新板卡通用规则”；已有板卡仍保留 button/USB-UART/PSRAM/SD 的有无期望与 revision/runtime
   组合文件名期望。
4. `targets.json` 仅记录例外：无条目的板卡使用默认值；有 `detect_class`、`probe_pins` 或
   非空 `wiring_fields` 时默认输出 `<chip>_wiring.hpp`；`specs_output` 仍需显式开启。
   拒绝空条目、显式默认值、未知字段、`specs_output` 无 wiring、device choice 内的
   `detect_class`。带非 `construct_displayless` 构造器的板卡仍必须有非空 `wiring_fields`
   （`m5atom_psram` 为显式例外）。

## 验证环境

- macOS arm64，Apple clang，Node 26.13.1。
- PR head 与 base 各一个 `git worktree`，均为 `m5stack/M5GFX` 公开仓库。
- Device Service 探测到 36 个 profile（`cores3` / `sticks3` / `cardputer-adv` /
  `paperdiy` 均存在），但本改动无运行时路径，未创建虚拟设备。

## 执行过程与结果

### 1. 仓库自带测试（head / base 对照）

```
head a092ea5  node cli/spec.js check  -> check passed: 64 board(s), 91 resolved combination(s)
head a092ea5  npm test                -> tests 238, pass 233, fail 0, skipped 5
head a092ea5  sh test/board_detect/run.sh -> C++ test programs: 34 passed

base 28b8a5c  node cli/spec.js check  -> check passed: 64 board(s), 91 resolved combination(s)
base 28b8a5c  npm test                -> tests 222, pass 217, fail 0, skipped 5
base 28b8a5c  sh test/board_detect/run.sh -> C++ test programs: 34 passed
```

5 项 skip 均为本机缺 M5Unified checkout（pin table 对比），base 与 head 一致。新增 16 项
测试，无失败、无新增 skip。

### 2. `npm run verify`

```
Catalog check: passed
Node tests: passed
C++ host tests: passed
```

`cli/verify.js` 会在 `check` 或 Node 测试失败后继续执行后续门禁，并且从环境删除
`M5GFX_UPDATE_SNAPSHOTS`，因此 verify 不会顺手更新快照。显式 `CXX=/nonexistent-compiler`
时输出 `C++ host tests: failed (... explicit CXX ...)`；无编译器且非 CI 时 skip 并提示。
这些分支都有 `test/verify.test.js` 覆盖（fixture 用假 `run.sh` 验证快照变量被删除）。

### 3. 生成物等价性

对 20 个变更头文件（19 个 `src/board_detect/m5/generated/*.hpp` +
`test/board_detect/generated/detector_probe_pins.hpp`）逐个比较“去掉注释行后排序的声明集合”，
全部相同。唯一的内容顺序变化是 `esp32p4_board_data.hpp`：两个 `unitpoep4*` 命名空间从
文件开头移到末尾（因为它们不再有 `targets.json` 条目，按 catalog ID 追加）。其余头文件
只改了重生成提示注释。`git diff` 中 `src/lgfx/boards.hpp` 仅新增一行注释。

### 4. 新增板卡工作流实验

从 `m5nanoc6.json` 复制一个 `m5trialc6`（BID 159、无屏、`construct_displayless`），只改：

- `extras/board_spec/boards/m5trialc6.json`（新文件）
- `src/lgfx/boards.hpp`（新增 enum）
- `src/board_detect/m5/esp32c6.inl`（`desc_trialc6` + `esp32c6_boards[]` 表项）

结果：

```
node cli/spec.js check  -> boards/m5trialc6.json is not formatted
                           Run "npm run generate" in extras/board_spec, then "npm run verify".
npm run generate        -> generated docs for 65 board(s) ...
node cli/spec.js check  -> check passed: 65 board(s), 92 resolved combination(s)
npm test                -> tests 238, pass 233, fail 0, skipped 5
git status              -> 只有上述 3 个文件（无 targets.json / test/* 改动）
```

说明 PR 的核心承诺对“无屏 / 无 targets 条目”的板卡成立；格式化失败信息也能直接指向
生成命令。

### 5. 显示构造器守卫

反向验证：临时删除 `targets.json` 中 `m5atoms3` 的条目，`npm test` 报

```
m5atoms3: construct_atoms3 requires nonempty wiring_fields in targets.json describing the
C++ descriptor reads; inferred wiring output alone is insufficient (see README.md, Adding a board)
```

这是设计内行为（README 已写明“Display boards normally need this metadata”），但说明
PR 正文 “targets.json records exceptions only / trial board passes without editing
targets.json” 的口径比实现宽，建议在描述里限定为“无 targets 字段需求的板卡”。

### 6. 失败诊断质量

- 删除两个生成头文件：`check` 一次列出两条 `missing generated artifact`，最后给出
  `Run "npm run generate" ... then "npm run verify".`，退出码 1。
- 向生成头追加一行：`stale generated artifact` + 同一提示。
- 在生成目录放一个多余 `.hpp`：`obsolete generated artifact` + 提示。
- 故意改 `test/board_detect/fixtures/c6.txt` 第 3 行：host 测试输出
  `Descriptor snapshot mismatch: test/board_detect/fixtures/c6.txt:3`、
  `expected:` / `actual:` 与 `M5GFX_UPDATE_SNAPSHOTS=1 ...` 提示。

### 7. editor 与 `dist/`

- `npm run editor` 生成 859,038 字节的 `dist/board_spec_editor.html`，`git status` 仍为空
  （`.gitignore` 生效）。
- `npm run generate` 前后工作区无差异，说明生成物是提交物而非手改。
- 全仓搜索 `board_spec_editor` / `extras/board_spec/dist`：除 README 与 `build/bundle.js`
  的本地构建说明外无引用，删除跟踪文件不会留下失效链接；也没有 CI/Pages 步骤依赖它。

### 8. 上游 CI

`gh pr checks 450`：39/39 pass，含 `host`、`Catalog and generated sources`、
ESP32/ESP32-S3/C3/C5/C6/C61/H2/P4 的 IDF 与 Arduino 矩阵、`translation unit consistency`。

## 评审结论

无阻塞问题。实现与 README 一致，`generate`/`verify`/诊断信息按描述工作，生成头文件只有
顺序与注释变化，host 套件无回归。两条非阻塞建议：

1. PR 正文把 “targets.json records exceptions only” 写成普适规则，实际显示类板卡仍需
   `wiring_fields` 条目；建议限定措辞，避免新贡献者漏条目。
2. 正文 “ordered by catalog ID” 应改为“已有条目保持 targets.json 顺序，无条目的按 catalog ID
   追加”；另新增的根级 PR 模板会作用于全部 PR，确认是否预期。

## 未覆盖项与风险

- `hardware validation` / `virtual-device validation` 均 `NOT RUN`：没有固件运行路径，
  虚拟设备无对象可观测；这不是缺少 profile。
- M5Unified live pin table 对比 `NOT RUN`（缺 checkout），base 同样 skip。
- 未在 ESP-IDF / Arduino 全矩阵本地重跑，采用上游 CI 结果作为覆盖证据。
- 本改动删除跟踪的 editor bundle，若仓库外有人以 raw/GitHub Pages 方式直接打开该文件会失效；
  仓库内无此引用，README 改为本地构建。记录为兼容性提示，不是本 PR 的阻塞项。

## 回滚

纯工具与生成物改动，回滚 PR 即可恢复 `dist/` 跟踪与旧测试清单；无迁移或运行时状态。
