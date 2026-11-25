# StackChan Issue #139 pt-BR 语言请求 — 完整分析

## 1. 问题与目标

m5stack/StackChan#139（作者 `ivenaaguiar`，2026-11-25T02:19Z，OPEN，创建时 0 评论）请求为
StackChan 的 AI Agent 增加巴西葡萄牙语（pt-BR）支持，包含三件事：语音识别、葡萄牙语 TTS 音色、
以及 StackChan World App 中的语言选项。

作者给出一条线索：App 的 `app/lib/util/value_constant.dart` 语言表里已经有
"Portuguese Português"，但 Agent Setting 里看不到该选项，怀疑是服务端尚未提供葡语音色。

目标：在不使用他人账号、不修改任何仓库的前提下，判断这个请求在代码里受什么控制、App 侧能否
自行修复、以及还缺什么，并给出可复核的边界说明。

## 2. 方法与取证环境

- 源码：只读 sparse clone `https://github.com/m5stack/StackChan`，HEAD
  `28b9f0c8bd6acd81cb3c70f1a93c3e373b39d400`（main，v1.6.2 合并提交，2026-11-04），
  只检出 `app`、`firmware`、`server` 三个目录。
- 本机 Device Service：只读查询 `GET /api/v1/devices`，实时列表中存在 `stackchan`
  profile（`simulated`，ILI9342C 320×240，touch，`backend_ready=true`）。
- 语音目录接口：未认证 `GET https://xiaozhi.me/api/user/tts-list` 返回
  `401 {"success":false,"message":"No token provided"}`。没有使用、借用或保存任何账号凭据，
  因此真实语言 key 集合不可见。
- 未构建、未运行 Flutter App；未连接实机；未启动虚拟设备会话。

## 3. 代码路径

### 3.1 语言下拉 = `tts_voices` 的 key 集合

`app/lib/view/popup/edit_agent.dart:88-91`：

```dart
// Load TTS data and build the language list from it.
Future<void> loadTtsList() async {
  ttsData = await XiaoZhiUtil.shared.getTtsList();

  // The language list is derived from the ttsVoices keys.
  if (ttsData?.ttsVoices != null) {
    languageList.value = ttsData!.ttsVoices!.keys.toList();
  }
```

选择器直接把这个列表渲染成选项（`edit_agent.dart:432-449`，`items: model.languageList.map(...)`,
选中后写回 key 本身）。欢迎页 `xiaozhi_welcome_page.dart:163-169` 使用同样来源。

### 3.2 `value_constant.dart` 只是显示名映射

`app/lib/util/value_constant.dart:163-205` 是 `Map<String, String>`，注释写明
"Key: Language code (ISO 639-1) / Value: Display name in English and native language"，
`"pt": "Portuguese Português"` 位于 `:180`。全仓库对它的引用只有两处，且都用于把 key 翻译成
显示名（`edit_agent.dart:246-252`、`xiaozhi_welcome_page.dart` 的同名函数）；未收录的 key 直接
回退显示原始 code。

所以：**往映射表里加条目不会产生选项**，作者的判断在这一点上是正确的。

### 3.3 目录来源与提交路径

- App 直连 `https://xiaozhi.me/`（`app/lib/util/xiao_zhi_util.dart:33`），
  以 `GET api/user/tts-list` 取目录（`:258-259`）。
- 访问该接口用的令牌由 StackChan 服务端下发（`app/lib/network/urls.dart:137`
  `xiaozhi/token`，App 侧 `XiaoZhi_util.dart:144` 取用）。
- 选中的 key 在创建/更新 agent 时作为 `language` 字段提交：`edit_agent.dart:203`
  （`language: selectedLanguage.value`）、`xiao_zhi_util.dart:309`（`POST api/agents`）。

即语言可用性取决于该令牌背后开发者账号在 xiaozhi 平台上的语音目录，而不是 App 本地维护的列表。

### 3.4 服务端同源，且比 App 多合并一份列表

`server/internal/xiaozhi/xiaozhi.go:46` 定义 `ttsList = "api/user/tts-list"`，`:273-281`
的 `GetTTSList()` 复用它；`server/internal/service/agent.go:128-160` 在恢复默认 agent 时，
把响应里的 `languages` 数组和 `tts_voices` 的 key 合并成候选语言集合，再挑可用音色。

App 端只用了 `tts_voices` 的 key。如果目录里某语言只出现在 `languages` 而没有对应音色条目，
App 下拉不会显示它。这是客户端与服务端的一处不对称，可以作为后续改进点，但**没有证据**表明
它是本次 pt 缺失的原因（真实目录不可读）。

### 3.5 固件 UI 的葡萄牙语是另一条路径

`firmware/main/Kconfig.projbuild:83-84` 提供 `LANGUAGE_PT_PT "Portuguese"`，
`firmware/main/CMakeLists.txt:192-193,243` 把它映射到 `assets/locales/pt-PT/language.json`。
这些 locales 资源由 `firmware/fetch_repos.py` 从上游 xiaozhi-esp32 拉取，不在本仓库内。

这是设备界面文案语言，与 AI 对话的 ASR/TTS 语言是两条独立路径；固件里有 pt-PT 选项不能推出
对话已支持葡语，反过来也不影响对话语言由服务端目录决定这一事实。

## 4. 结论与边界

1. pt-BR 的“选项没出现”不需要改 App 代码：目录一旦返回 `pt` 音色，下拉会自动出现，显示名也已经
   备好（`value_constant.dart:180`），未收录的 key 也不会导致崩溃。
2. 阻塞点在上游语音目录 / 账号能力：既要有葡萄牙语音色，也要有 ASR 侧对葡语的支持。两者都不是
   StackChan App 本地能开启的。
3. 设备界面语言已支持 pt-PT，用户可以先得到葡语界面；对话语言仍取决于平台侧开通。
4. 无法从公开信息判断该账号何时会加入 pt/pt-BR，也无法验证音色质量与 ASR 识别效果，因此不给出
   时间承诺，也不宣称平台已支持。

## 5. 未覆盖项

- 硬件验证 `NOT RUN`：问题位于 Flutter App 的 Agent Setting 页面与远端目录，实机不经过该路径，
  也没有可用的已登录账号。
- 虚拟设备验证 `NOT RUN`：本机存在 `stackchan` profile，但它复现的是固件运行时，不执行 App 的
  Agent Setting 页面，也不持有 xiaozhi 令牌，无法验证语言下拉与音色。
- 真实目录内容未读取（401，无凭据）；未构建/运行 App；未验证葡语音色可用性、延迟、音质；
  未验证 ASR 对 pt-BR 的实际识别质量；未查阅上游平台对葡萄牙语的公开说明，避免在无访问条件下
  做能力推断。

## 6. 处理方式

只向原 issue 发布一条英文回复（跟随原帖语言）：
https://github.com/m5stack/StackChan/issues/139#issuecomment-7150663269

回复内容：

- 确认作者判断：下拉由 `tts_voices` key 驱动，`value_constant.dart` 只是显示名，加条目不会产生选项；
- 给出数据来源、提交路径与服务端同源代码位置；
- 说明固件 UI 的 pt-PT 是界面语言，与对话语言无关，可作为过渡；
- 指出 App 只取 `tts_voices`、服务端合并 `languages`+`tts_voices` 的不对称，以及 `pt-BR` 独立 key
  会先以原始 code 显示，作为后续改进点而非本次原因；
- 明确 `code-level verification` 层级与 `NOT RUN` 项，未给时间承诺。

issue 保持 OPEN，未关闭、未改动任何仓库。
