# 技术报告

## 目标与验收范围

本条接续原版 S3-watch 只观察到 WEB 地址、尚无匹配认证 HTTP 证据的阶段。相同原版在本机隔离原生路径完成了目标 WPA2 与固定 HTTP 只读请求，错口令负控和维护版 runner 也已执行。总体保留 `PARTIAL`，因为组合 runtime 的旧 StopWatch 兼容性对照尚未闭合；没有主线提升或常驻部署。

原版为 S3-watch 0.1 (worked)，8,388,608 字节，SHA-256 `eb7f9425c07cffd972d0de479fc6c82d86af2aa51dc807d9829d5ee55add163b`。原应用未修改；没有时钟夹具、时钟写入、A 输入、HTML 执行或 guest HTTP 写操作。原始代码和配置含敏感内容，归档仅使用已脱敏摘要。

## 精确实现身份

本地源码提交 `073104c072ebfab24ed010216a6ea24e0ba4ea4e` 尚未推送公开项目。API 契约摘要为 `2bdcdbd42af109fcf93c149c859e02eec28cb8b77d735991c46b7f70bd3cf51b`。本条不提供未发布提交的失效链接，也不把工作记录发布等同于产品发布。

执行使用明确的 `sticks3-s3-watch-wpa2` profile，macOS arm64、xtensa-softmmu，完整 180 层前缀的独立原生构建。二进制 SHA-256 为 `67e78237fe35a1b81b0e2e3070c72b7e415dc4bf22e3506162c78a2c51da609a`，ROM 为 `b5c7090cc22efce51c1323cef31ca96fcd673a5b1d1b1017e219d393f2659913`；补丁 0234 为 `97c2a9cb9f6b34704f0c59e57618df0111b73b78bdc5500198c758d99e80fe13`，source manifest 为 `457a3ab7401cec2501769962703a8716dcdb165bbfe3e0903e0d9b30081dc1d8`。详细 build/bootstrap 与实际 C 控制身份见摘要。

数据面通过私有 Unix socketpair，宿主 IP 后端为零，不访问外部网络。凭据仅在本地请求范围内使用，记录不保留其值。这里验证 emulated controller/data plane，未证明物理 RF、安全认证、实时性或不可信固件沙箱。

## 初始状态与 B 关/开

会话创建后先等待并按固定间隔取样。成熟初始画面已有 WEB 地址，但实际初始 beacon 的目标身份不匹配、Privacy 未置位且无目标 RSN；画面地址本身不能证明目标 WPA2 已接通。

第一次 B 长按 2 秒、settle 1 秒后观察 WEB OFF；第二次相同长按后观察目标 Privacy、CCMP/PSK RSN 与 WEB 地址。记录证明这些实际关/开转换，没有把首个 WEB 地址或第一次启动分支的原因作过强归因。未定位固件或 SDK 根因。

## 强正控与错口令控制

正控九项门控均通过：peer DHCP、ARP、HTTP body，抓包 DORA/HTTP，当前 WPA2 association、guest handshake，以及 protected guest TX/RX。QOM M1/M2/M3/M4 各为 1，protected TX/RX 为 11/7，ready 为 true。固定 `GET /api/state HTTP/1.0` 收到 200、152 字节 JSON，body SHA-256 为 `0e319e2fe6ed2cf97f0b66c84c435e4c659668586072f0ef0cf2a1eba107df68`。

同会话最终抓包 `7ca0224ab8a34cb57bf6f3fe7c39d45ff10175757c1258583bf7cacbfdfd45c1` 为 7,899 字节；停止后派生计数为 1 次完整 DORA、1 个地址、1 条双向 TCP payload 流。维护版 runner 在同一原版上重复通过，抓包身份另存于摘要。

错口令运行的 peer 原状态保持 `PARTIAL`，预期拒绝这项负控为 `PASS`。它观察到 M1/M2 各 27 次，M3/M4 为零，ready 为 false，protected TX/RX、DORA、双向 TCP 与 HTTP 均未出现。格式化 runner 对该预期拒绝返回 exit 0；这不表示错误口令连接成功。

停止前 ZIP 中摘要仍可能是 `CAPTURING`。本条最终 DORA/TCP 取停止后的同会话 API 与停止 ZIP，早期原始 PCAP 字节与最终解析输入的 SHA 相同。归档没有读取或发布这些 ZIP 字节，使用 case owner 和独立核验给出的有界摘要与哈希。

## 早期结果与时钟 oracle

阶段2 A1 抓包实际已收到 HTTP 200、152 字节 JSON，但首版 oracle 拒绝原版合法的未校时时间占位 `--:--:--`。该次应用 oracle `FAIL` 保留，不改写为当时完整验收通过。后续没有施加时钟设置或时钟 fixture，也未证明外网校时。

此前非目标初始 beacon、过严 RSN 可选字段检查、discovery socket 背压，以及握手/受保护 DMA 已观察但尚未转发的数据阶段均保留；较早 B1 的功能正控发生在最终诊断日志清理与 runtime 冻结前，最新强正控及维护 runner 使用最终固定二进制。后来的通过不覆盖先前结果。

## 组合 runtime 的兼容性阻塞

在组合 `67e78237…` 上，旧 StopWatch 第一次短观察与后一次 60 秒脚本均完成门户 HTTP，但未完成 STA DHCP/ARP；同当前 Device Service、原版、ROM、配置和 60 秒脚本的 `5b8b3f24…` 基线通过，记录 2 次 DORA 和 4 条双向 TCP payload 流。

后续只打开现成 Wi-Fi trace，没有重建或修改任一二进制，两版均通过。两版都观察到 management subtype 10 两次、12 一次。这些通过的 trace 不能解释或消除先前未开 trace 的差异；串口断开也不能替代实际发出的 deauthentication 帧证据。原因未定位，不作 reset-cause、固件故障或确定补丁根因归属，组合提升继续 `BLOCKED`。

此前[StopWatch 出厂配网独立记录](../2026-11-23-stopwatch-factory-provisioning/)的精确二进制验收仍独立成立；本条没有把它迁移为新组合的完成证明。

## 测试、清理与剩余范围

最终完整平台 2529 项、11 跳过、0 failure/error，221.812 秒；日志 SHA-256 为 `a1549400256232414af6573e0368a3f421ab12d5b9503d328c910b38dec6bb41`。7 项 focused、22 项文档检查及四校验器通过；此前 4 项 WIP 文档/快照失败保留。实际 C 控制的 ASan/UBSan、known-answer、错误 key/ciphertext/MIC、RSN/长度/缓冲及 guest key-table/重放边界检查通过，leak check 未运行。测试绿灯不替代上述组合功能阻塞。

各 case 已保存停止前证据，停止后再核最终摘要；peer 释放、Flash 释放、会话与 owned 测试服务停止、租约归零，trace 诊断也已完成。原始抓包、帧、ZIP、配置和敏感源码留在私有证据层。

只覆盖非 QoS data subtype 0、AP 发出的 IPv4/ARP、CCMP-128/PSK、PMKID count 为零及非零 GTK index。PMF、其他密码套件、通用桥接、广泛 rekey 互操作、Linux、浏览器、常驻、物理 RF/功耗/时序/安全与外网均未验收；Reviewer 自动输入编排是独立工作，未提交 Burner。回退边界为保持候选不提升并沿用既有固定生产 runtime，本条没有执行生产替换。
