# M5GFX PR #439 评审报告

## 1. 问题背景与目标

issue #436：ToughC5 のタッチ（`Touch_CHSC6540`）が ACK 終端で読むため、LP I2C ポートでは
`endTransaction()` の STOP が完了せず、`i2c_stall_limit_us`（25 ms）待って
`connection_lost` を返していた。`M5.update()` が毎回 37.8 ms（IDF 5.5.4）/ 25.8 ms（6.1）
止まる。

本 agent は 2026-11-19 に、LP の `endTransaction()` で「直前の read が ACK 終端のときだけ
STOP の前に `READ 1 byte + NACK` を入れる」案 B を提示し、maintainer（ainyan03）が
2026-11-20 に案 B・HP と NACK 終端を変えないスコープで承認した。

PR #439 はこの案 B の実装。本记录的目标是核对差分是否正确实现该范围，以及是否引入新的
回归面。

## 2. 差分核对

变更：`src/lgfx/v1/platforms/esp32/common.inl` のみ、26 追加 / 2 削除。
相对当前 develop tip `43a87193` 的 diff 与本 PR 的 diff 完全一致（无额外改动、无需 rebase）。

### 2.1 状态管理（4 个置位/清除点）

| 位置 | 内容 | 核对 |
| --- | --- | --- |
| `:1713` | `bool last_read_acked` を `i2c_context_t` に追加 | 追加のみ、他フィールド不变 |
| `:2900` | `if (res.has_value()) last_read_acked = !last_nack;` | 成功時のみ、`last_nack` を反映 |
| `:2822` | `readBytes()` 冒頭で `false` | `if (!length) return` より後。0 长 read は直前の値を保持するが、それは直前の read を閉じる対象として正しい |
| `:2626` | `restart()` で `false`（`beginTransaction()` は必ず `restart()` を呼ぶ） | 前トランザクションの値が持ち越されない |
| `:2132` | STOP 分岐の最後で `false` | 成功・STOP 失败のどちらでも到達 |

`readBytes()` が失败した場合（`:2840-2844`, `:2891-2894`）は冒頭の `false` のままで、
古い `true` は残らない。`writeBytes()` は `state == state_read` を拒否するため、
read の後ろに write が挟まってダミー read が误适用される経路もない。

### 2.2 条件とコマンド列

`:2098-2104` の条件は `isLpPort(i2c_port) && state == state_read && last_read_acked`。
`last_read_acked` は `!last_nack` なので、NACK 終端 read では常に false。
`force_stop_read`（`:2073`）は HP のみで、LP の強制停止分岐（`:2081-2088`）は従来どおり。

コマンド列は `nack_before_stop` のとき

    READ(byte_num=1, ack_val=1) -> STOP -> END

で、`i2c_set_cmd()` の `flg_nack` は read の ack_val（bit10）を立てる（`:1851-1856`）。
新 IP のコマンドレイアウト（byte_num[7:0] / ack_en[8] / ack_exp[9] / ack_val[10] /
op_code[11:13]）は IDF の `i2c_ll_hw_cmd_t` と一致する。

### 2.3 追加バイトの破棄

`:2126-2131` は STOP 完了後に RX FIFO を空にする。`readBytes()` はチャンクごとに要求
バイト数を読み切っており、FIFO に残るのはダミー read の 1 バイトだけなので、他のデータを
捨てることはない。STOP が失败した場合は直前に `i2c_stop()`（`:2123`）が走り、C5 / C6 / P4
では `i2c_periph_reset()` → `lp_i2c_periph_reset()` で LP ペリフェラルがリセットされるため
FIFO は空。コメントの記述と実装が一致する。

## 3. ESP-IDF による独立した佐证

ローカルの ESP-IDF v6.0.2 ソース（`components/esp_driver_i2c/i2c_master.c`）で確認:

1. `i2c_master_receive()`（`:1334-1345`）は
   `START -> READ(n-1, ACK) -> READ(1, NACK) -> STOP` を作る。つまり IDF 自身が
   「read の最終バイトは NACK、その直後に STOP」という並びを使っている。
2. `i2c_master_transmit_receive()`（`:1459-1470`）は、READ の次が STOP なのに
   `ack_val != NACK` の場合 `ESP_ERR_INVALID_ARG`（"ack_value must be NACK (1) when the
   next command of READ is STOP."）で拒否する。ACK 終端 read の直後に STOP を置けない、
   という PR の原因説明と一致する。
3. ISR（`:795-797`）は `nack_int` を ACK エラー（`I2C_STATUS_ACK_ERROR`）として扱うが、
   IDF の受信は常に最終バイトを NACK して成功する。したがって「マスターが送る NACK は
   ACK エラーを立てない」という PR のコメントは IDF の前提と矛盾しない。

## 4. 影響面

- LP I2C を持つ SoC は IDF v6.0.2 の soc_caps で ESP32-C5 / C6 / P4 の 3 機種のみ
  （ESP32-H2 は HP 2 本、ESP32-C61 は HP 1 本で LP なし）。PR 本文の実機 3 機種
  （ToughC5 / NessoN1 の C6 / Tab5 の P4）× IDF 2 バージョンが LP ポートの対象を
  すべて覆っている。
- M5GFX 自身の `transactionRead()` / `readRegister8()` / `writeRegister8()` は既に
  `last_nack=true` で読む（`:2931-2958`）。したがって本変更の主対象は `readBytes()` を
  既定（`last_nack=false`、`src/lgfx/v1/platforms/common.hpp:275`）で呼ぶ外部ドライバで、
  #436 の `Touch_CHSC6540` がこれに当たる。
- 副作用（ACK を受けたスレーブが次のバイトを用意し、読み出し位置や FIFO が進みうる）は
  閉じ方によらず残る。PR 本文に明記されており、恒久対策はドライバ側で最終バイトを
  NACK すること。本 PR は 25 ms 待ちを消すことに限定している。

## 5. 执行与证据

- PR head `4b012d6e691b9d6281c244e7bb212169dd97e7f6`、base / develop tip
  `43a87193f898f998edf79c5fb99b166d11ee1eaf`。`common.inl` の差分は 26/2 で PR と一致。
- 上游 CI（GitHub Actions）: 38 チェックすべて SUCCESS。ESP-IDF 5.1.6〜6.x、
  Arduino コア、esp32c5 / esp32c6 / esp32p4 / esp32h2 を含む。コンパイルのみ。
- 当方的验证: code-level verification のみ。

## 6. 未覆盖项与风险

- hardware validation `NOT RUN`：C5 / C6 / P4 实机なし。PR 表の 46〜75 µs、
  `M5.update()` 約 1.0 ms は作者計測で、本记录未复测。
- virtual-device validation `NOT RUN`：Device Service 36 profile に C5 なし、tab5 は
  `tab5_enabled=false`、esp-emulator に LP I2C 控制器模型なし。
- maintainer 承诺的 C6 / P4 回归 `NOT RUN`（第三方计划）。
- 残余风险：ダミー read 中にスレーブが SCL をストレッチし続ける場合、従来と同じく
  25 ms 待ち→`i2c_stop()` に落ちる（退行ではないが、改善もしない）。
- 回滚：本 PR を revert すれば #436 の 25 ms 待ちに戻る。他路径への変更はない。

## 7. 已发布回复

- PR #439 へのコメント 1 条（日文）。内容：差分核对の結論、code-level verification、
  上游 CI 38/38、未覆盖项（hardware / virtual-device `NOT RUN`）。
  <https://github.com/m5stack/M5GFX/pull/439#issuecomment-7093676522>
- PR は OPEN のまま。close・push・他人リポジトリ変更はしていない。
