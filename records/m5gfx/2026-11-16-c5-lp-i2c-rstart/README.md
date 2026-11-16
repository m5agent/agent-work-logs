# ESP32-C5 LP_I2C: 2 バイト書き込み直後の RSTART 読みが無言で失われる（M5GFX #421 コードレベル調査）

- 日付：`2026-11-16`
- 結果：`PARTIAL`（コード読解のみ。物理ハードウェア・仮想デバイスとも `NOT RUN`）
- 種別：`issue`
- 問題：[m5stack/M5GFX#421](https://github.com/m5stack/M5GFX/issues/421)
- 対象ソース：M5GFX `master` `28d47949bdc84f30881623476f555398e2194313`（0.3.0）、
  `develop` `b48dce0`、ESP-IDF `v5.5` の ESP32-C5 ヘッダ／`i2c_master.c`
- GitHub 返信：投稿済み 2026-11-16（[issuecomment-6911970836](https://github.com/m5stack/M5GFX/issues/421#issuecomment-6911970836)）。issue は OPEN のまま
- 環境：macOS。本機に ESP32-C5 実機なし。Device Service に C5 プロファイルなし。
  esp-emulator のランタイムに I2C コントローラのモデルなし。

## 結論

報告のコード経路は M5GFX の LP I2C 実装で特定できた。LP ポートは ESP-IDF でバスを開いた
あと、HP ポートと同じレジスタ操作で転送する。1 回の論理転送は
「アドレス → データ → RSTART+アドレス → 読み出し」の 4 つのコマンド列に分割され、
各列の末尾は `END`（SCL を保持して停止）で、STOP は `endTransaction()` まで出ない。
報告の失敗点（2 バイト書き込みの直後の RSTART）は、この分割の境界そのものである。

`writeBytes()` は自分が起動した転送の完了を待たずに戻る（先頭の `i2c_wait()` は前の列の
完了待ち）。完了判定は次の呼び出しの `i2c_wait()` で `END_DETECT` と NACK だけを見ており、
TX FIFO に未送出バイトが残っていないかは確認しない。したがって「2 バイト目が送られていない」
場合でも各呼び出しが成功を返すことはコード上あり得る。報告の「無言」と整合する。

原因の確定はできていない。C5 実機も LP_I2C を模擬する仮想デバイスもないため、未確認の
候補機構と、それを切り分ける実験を返信にまとめた。

## コード上の事実（`28d4794`）

- LP ポートの初期化は `i2c_new_master_bus()`（`lp_source_clk = LP_I2C_SCLK_XTAL_D2`）に
  任せ、そのあとレジスタを直接操作する：`common.inl:2146-2166`（`lp_source_clk` は `:2154`）。
- `restart()` は `[RSTART, WRITE(addr), END]` を組んで `trans_start` する：`:2232-2358`。
- `writeBytes()` は先頭で前の列の `i2c_wait()` を呼び、`[WRITE(n), END]` を組んで
  `trans_start` した直後に戻る：`:2501-2537`（`trans_start` は `:2534`）。
- `readBytes()` は `[READ…, END]` を組む。1 バイト読みは `READ(1, NACK)` になる：`:2542-2591`。
- 完了判定は `END_DETECT` が立ち、NACK／タイムアウト／調停喪失がないことだけ：`:1827`。
- 読み出し後の `endTransaction()` は `state == state_read` のため強制 STOP 経路に入り、
  GPIO ビットバング STOP のあと `lp_i2c_ll_reset_register()` で LP ブロックをリセットし、
  保存レジスタを書き戻す：`:1877`、`:1736-1772`、`:1469-1483`、`:2476-2484`。
- LP の FIFO 長は `SOC_LP_I2C_FIFO_LEN` = 16 バイトで、`getFifoLen()` は LP で 16 を返す
  （`common.inl:1347-1355`）。2 バイトが `writeBytes()` 内で分割されることはない。

## ESP-IDF v5.5（ESP32-C5）との差

- `components/soc/esp32c5/include/soc/soc_caps.h` に `SOC_I2C_STOP_INDEPENDENT` はない
  （`SOC_LP_I2C_FIFO_LEN` = 16、`SOC_I2C_CMD_REG_NUM` = 8、`SOC_LP_I2C_SUPPORTED` = 1）。
- `components/esp_driver_i2c/i2c_master.c` は、その場合に
  `RSTART → WRITE(addr+data) → RSTART → READ → STOP` を **1 つのコマンド列**に組み、
  1 回の `trans_start` で実行する（`:204`、`:294`、`:1199-1212`）。
- M5GFX のように転送の途中でコマンド列を区切って CMD コントローラを再起動する経路は、
  IDF のマスタードライバでは使われていない。

## 未確認の候補（断定しない）

1. `END_DETECT` を「データ列の完了」とみなして RSTART に進むため、最終バイトがまだ
   FIFO／シフトレジスタにある段階で次列を書いてしまう。
2. LP の FSM で、RSTART を伴わない `WRITE` からの再開が HP と異なる振る舞いをする。

報告の表（1 バイト+RSTART は通る／2 バイト+STOP は通る／2 バイト+RSTART だけ落ちる）は
どちらでも説明できる。切り分けは返信に書いた 2 つの実験（RSTART 前の遅延、IDF ドライバでの
同一シーケンス）で行う。

## 未カバー

- ESP32-C5 実機での再現、LP_I2C レジスタダンプ、SDA/SCL 波形
- 仮想デバイス（C5 プロファイル／I2C モデル）での再現
- develop の初期化時スプリアス START 修正（PR #398）が本件に与える影響
- 修正案の実装と検証

## ファイル

- [report.md](report.md)：コード事実、IDF との比較、切り分け手順、返信文
- [run.json](run.json)：構造化ステータス
- [evidence/lp-i2c-sequence.txt](evidence/lp-i2c-sequence.txt)：`28d4794` からの該当コード抜粋
- [evidence/source-pins.json](evidence/source-pins.json)：固定 commit とファイル SHA256
