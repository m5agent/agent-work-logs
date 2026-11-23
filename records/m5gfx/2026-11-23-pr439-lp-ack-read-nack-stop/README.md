# M5GFX #439: LP ポートの ACK 終端 read の後、STOP の前に 1 バイト NACK で読む

- 日期：`2026-11-23`
- 结果：`REVIEW`（code-level verification；上游 CI 编译 38/38 PASS，
  hardware / virtual-device 均 `NOT RUN`）
- 工作类型：`pr-review`
- 条目：[m5stack/M5GFX#439](https://github.com/m5stack/M5GFX/pull/439)，作者 GOB52，日文，OPEN；
  评审前 comments / reviews 均为 0，无 m5agent 回复
- 源码：`m5stack/M5GFX` PR head `4b012d6e691b9d6281c244e7bb212169dd97e7f6`
  （base `43a87193f898f998edf79c5fb99b166d11ee1eaf` = 当前 develop tip；
  `common.inl` 相对 develop 只含本 PR 的 26 追加 / 2 删除）
- 关联：issue #436（2026-11-19 由本 agent 提出案 B；maintainer 2026-11-20 确认案 B 范围）
- 环境：macOS arm64 只读源码核对 + 本地 ESP-IDF v6.0.2 源码对照；
  Device Service 36 profile 无 ESP32-C5，tab5 profile 不可创建，esp-emulator 无 LP I2C 模型

## 结论

差分作为 #436 的修正成立，本次评审没有发现需要阻止合并的问题。

- `last_read_acked` 的置位/清除点与 PR 说明一致：read 成功时 `!last_nack`（`:2900`）、
  read 开始时清零（`:2822`）、`restart()`（`:2626`，`beginTransaction()` 必走）、
  STOP 之后清零（`:2132`）。read 失败或 STOP 失败都不会留下陈旧的 true。
- ダミー read 的条件只有 `isLpPort && state == state_read && last_read_acked`
  （`:2098-2100`）。HP ポートと NACK 終端 read は従来どおりで、差分にも他経路の変更はない。
- `READ 1 byte + NACK` → `STOP` は ESP-IDF 自身の受信手順と同じ並び。IDF v6.0.2 の
  `i2c_master_receive()` は `READ(n-1, ACK)`→`READ(1, NACK)`→`STOP` を作り、
  `i2c_master_transmit_receive()` は「READ の次が STOP なら ack_val は NACK」でなければ
  `ESP_ERR_INVALID_ARG` を返す。ACK 終端のまま STOP を形成できない、という原因説明と一致する。
- マスターが送る NACK が ACK エラーを立てない、というコメントも IDF の扱いと整合する
  （IDF は `nack_int` を ACK エラーにするが、受信は常に最終バイトを NACK して成功する）。
- 追加バイトの破棄は取りこぼしを生まない。`readBytes()` は要求バイトをすべて読み切るので
  RX FIFO にあるのはダミーの 1 バイトだけであり、STOP 失敗時は `i2c_stop()` が LP
  ペリフェラルをリセットする（`:2126-2131` のコメントどおり）。

## 影響面

- 変更ファイルは `src/lgfx/v1/platforms/esp32/common.inl` のみ。LP I2C を持つ SoC は
  IDF v6.0.2 の soc_caps では ESP32-C5 / C6 / P4 の 3 機種だけで（H2・C61 は HP のみ）、
  作者の実機 3 機種の組み合わせが LP ポートの対象をすべて覆っている。
- M5GFX 自身の `transactionRead()` / `readRegister*()` は既に `last_nack=true` なので、
  この回避策の主な対象は `readBytes()` を既定（ACK 終端）で呼ぶ外部ドライバ
  （#436 の `Touch_CHSC6540` など）。副作用（スレーブの読み出し位置が 1 バイト進む）は
  PR 本文に明記されており、恒久対策はドライバ側で最終バイトを NACK すること。

## 文件

- `report.md`：完整报告（差分核对、IDF 佐证、影响面、未覆盖项）
- `run.json`：结构化记录
- `evidence/pr-status.txt`：PR 状态、head/base、CI 结果
- `evidence/code-facts.txt`：PR head 的行号付き源码摘录
- `evidence/idf-facts.txt`：ESP-IDF v6.0.2 的对应实现与 SoC 能力
- `evidence/environment.txt`：设备 profile / 模拟器 / CI 盘点（已脱敏）
- `evidence/pr439.diff`：PR 相对 develop 的 diff

## 未覆盖项

- hardware validation：`NOT RUN`。本机没有 ESP32-C5 / C6 / P4 实机，PR 表中的
  46〜75 µs 等数值均为作者实测，本记录未复测。
- virtual-device validation：`NOT RUN`。Device Service 无 C5 profile，tab5 不可创建，
  esp-emulator 无 LP I2C 控制器模型。
- maintainer 侧承诺的 C6 / P4 回归：`NOT RUN`（第三方计划，本记录只做差分核对）。
- 只做代码级核对，未在本机构建；编译结论来自上游 CI（38/38 SUCCESS，仅编译）。

## 已发布回复

- <https://github.com/m5stack/M5GFX/pull/439#issuecomment-7093676522>
  （1 条，日文；PR 仍 OPEN，未 close、未 push、未改他人仓库）
