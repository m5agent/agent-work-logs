# M5GFX #421 調査詳細：ESP32-C5 LP_I2C の分割コマンド列

- 対象：M5GFX `master` `28d47949bdc84f30881623476f555398e2194313`（0.3.0）
- 比較：`develop` `b48dce0`、ESP-IDF `v5.5`（ESP32-C5）
- 実行検証：なし（物理 C5・LP_I2C モデルとも入手できない）
- 証拠分類：`code-level verification`

## 1. 報告の内容（要約）

ToughC5（ESP32-C5HR8、board id `0x21`）の Ex/In I2C は `LP_I2C_NUM_0`。
`start(addr, write) → write(2 bytes) → restart(addr, read) → read(1 byte)` のときだけ、
バスに何も書かれず、しかも全呼び出しが成功を返す。1 バイト書き込み + RSTART 読みは通り、
2 バイト書き込みを STOP で閉じて別トランザクションで読む場合も通る。
HP I2C の Core（board id `0x01`）では同じスケッチが通る。
単位は M5Stack UnitNFC（ST25R3916、`0x50`）で、Space A は 1 バイト選択、
Space B は 2 バイト選択という違いだけを使っている。

## 2. M5GFX 側の経路

LP ポートは ESP-IDF の `i2c_new_master_bus()` で開き（ピン、LP クロック源、
内部プルアップ）、そのあと I2C レジスタを直接操作する。HP ポートとの差は
FIFO 長（16 対 32）と、1 トランザクションごとに `set_pin()` を呼ばないことだけ。

1 回の論理転送は次の 4 つのコマンド列に分かれる。各列は `END` で終わり、
STOP は出さない（`END` は SCL を保持して停止するだけ）。STOP は
`endTransaction()` のときだけ出る。

| 呼び出し | コマンド列 | 備考 |
|---|---|---|
| `beginTransaction()` → `restart()` | `RSTART, WRITE(addr), END` | 実アドレスを送って止める |
| `writeBytes(n)` | `WRITE(n), END` | `trans_start` した直後に戻る |
| `restart()` | `RSTART, WRITE(addr\|R), END` | ここが報告の「repeated start」 |
| `readBytes()` | `READ…, END`（1 バイトは `READ(1, NACK)`） | |
| `endTransaction()` | `STOP, END` または強制 STOP | |

`writeBytes()` の戻り値は、ループ先頭の `i2c_wait()`（＝前の列の完了待ち）の結果で、
自分が起動した転送の結果ではない。データ列の完了は次の `restart()` の `i2c_wait()` で
判定される。`i2c_wait()` の成功条件は `END_DETECT` が立ち、NACK／タイムアウト／
調停喪失がないことだけ。TX FIFO に未送出バイトが残っていないかは見ていない。

つまり「2 バイト目が送られていない」場合でも、`write()` / `restart()` / `read()` が
すべて成功を返すことはコード上あり得る。報告の「無言」と整合する。

### 該当行（`28d4794`）

- `common.inl:2146-2166` LP 初期化（`lp_source_clk` は `:2154`）
- `common.inl:2232-2358` `restart()` のコマンド列
- `common.inl:2501-2537` `writeBytes()`（`trans_start` は `:2534`）
- `common.inl:2542-2591` `readBytes()` のコマンド列
- `common.inl:1827` 成功判定
- `common.inl:1877` 読み出し後の強制 STOP 分岐
- `common.inl:1736-1772` `i2c_stop()`（GPIO ビットバング）
- `common.inl:1469-1483` LP の `lp_i2c_ll_reset_register()`
- `common.inl:1347-1355` `getFifoLen()`（LP は 16）

### 関連する LP 固有の挙動

読み出しを含むトランザクションの `endTransaction()` は `state == state_read` のため
強制 STOP 経路に入る。ここでは GPIO を直接叩いて STOP を出したあと、
`lp_i2c_ll_reset_register()` で LP I2C ブロックをリセットし、`save_reg()` した
レジスタを `load_reg()` で書き戻す。報告の「各周回の最初の Space A 読みが `0xFF`」は
この経路と関係する可能性があるので、波形を取るなら読み出し直後も見てほしい。

## 3. ESP-IDF v5.5（ESP32-C5）との比較

- `components/soc/esp32c5/include/soc/soc_caps.h`：
  `SOC_I2C_NUM` = 2、`SOC_HP_I2C_NUM` = 1、`SOC_LP_I2C_NUM` = 1、
  `SOC_I2C_FIFO_LEN` = 32、`SOC_LP_I2C_FIFO_LEN` = 16、`SOC_I2C_CMD_REG_NUM` = 8。
  `SOC_I2C_STOP_INDEPENDENT` は定義されていない。
- `components/esp_driver_i2c/i2c_master.c`：
  `SOC_I2C_STOP_INDEPENDENT` が無いターゲットでは、RSTART → WRITE(addr+data) →
  RSTART → READ → STOP を 1 つのコマンド列に組み、`trans_start` は 1 回だけ
  （`:204`、`:294`、`:1199-1212`）。転送の途中でコマンド列を区切る経路はない。
- `components/hal/esp32c5/include/hal/i2c_ll.h`：
  `I2C_LL_CMD_RESTART` = 6、`WRITE` = 1、`READ` = 3、`STOP` = 2、`END` = 4。
  コマンド構造体は `byte_num:8, ack_en:1, ack_exp:1, ack_val:1, op_code:3, done:1`。
  M5GFX の `i2c_set_cmd()` と一致する。
- `i2c_ll.h` の `i2c_ll_set_source_clk()` は LP では何もしない（LP のクロック源は
  `LP_CLKRST.lpperi.lp_i2c_clk_sel`）。M5GFX は `esp_clk_tree_src_get_freq_hz()` で
  XTAL_D2 の周波数を取ってタイミングを計算しており、この点は IDF と矛盾しない。

## 4. 未確認の候補（断定しない）

1. `END_DETECT` をデータ列の完了とみなして RSTART に進むため、最終バイトがまだ
   FIFO／シフトレジスタにある段階で次の列を書き、RSTART が末尾を壊す。
2. LP の FSM で、RSTART を伴わない `WRITE` からの再開が HP と異なる。

報告の表（1 バイト+RSTART は通る／2 バイト+STOP は通る／2 バイト+RSTART だけ落ちる）は
どちらでも説明できる。1 は「RSTART の前に遅延を入れる」「2 バイト書き込みの直後に
`sr.txfifo_cnt` を見る」で、2 は「IDF ドライバで同じシーケンスを実行する」で切り分く。

## 5. 返信に書いた依頼

1. `write(sel, 2)` と `restart()` の間に `delayMicroseconds(50〜100)` を入れた結果。
2. 同じシーケンスを LP ポートで ESP-IDF `i2c_master_transmit_receive()` で実行した結果。
3. RSTART 直前の書き込み長 1/2/3/4 の境界（Space A の 3 バイト書き込み + RSTART 読みも）。
4. 使用した M5GFX / M5Unified の正確な commit と、可能なら SDA/SCL 波形。

## 6. 未カバー

- ESP32-C5 実機での再現、LP_I2C レジスタダンプ、波形取得
- 仮想デバイス（C5 プロファイル／I2C モデル）での再現
- develop の PR #398（初期化時スプリアス START 修正）が本件に与える影響
- 修正案の実装・ビルド・実機検証

## 環境メモ

- Device Service（`http://127.0.0.1:8787`）のプロファイルは C6 / P4 / S3 / ESP32 / LX6 系のみ。
- esp-emulator の wasm ランタイムに I2C の実装がない。
- ハードウェアテストセンターのノードは matrix / corep4 / sticks3 / stopwatch のみ。
