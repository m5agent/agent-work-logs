投稿: https://github.com/m5stack/M5GFX/pull/423#issuecomment-6922062344（2026-11-17、1 件のみ。PR は OPEN のまま）

## 結論

原因の説明は現在の `develop`（`b48dce0`）のコードと一致し、変更も最小で妥当です。LP ポートの「read で終わるトランザクション」だけがコントローラの STOP で閉じられ、HP ポート、write 終端、エラー時の強制 STOP は従来のままです。コードを見る限り、マージを止める理由は見つかりませんでした。

#421 でお願いした「コントローラ STOP 単独」の切り分けは、本文の 1 つ目の表（Space B の read 直後の Space A の read が `develop` 0/100 → この変更 100/100）で満たされています。ピンの貸し出しを含めない判断とも整合します。

確認をお願いしたいのは 1 点だけ、C5 以外の LP I2C チップでの read 終端です（下記）。

## 証拠レベル

code-level verification（`develop` `b48dce0` と PR head `cc60eaa` のソース読解）。当方の hardware validation / virtual-device validation / build は NOT RUN です（理由は末尾）。PR が `b48dce0` にクリーンに適用できることは確認しました（`git apply --check`）。

## コードで確認したこと（`develop` `b48dce0`）

- `i2c_stop()`（`src/lgfx/v1/platforms/esp32/common.inl:1847-1882`）は `gpio_set_level` / `gpio_set_direction` だけで STOP を作り、最後に `i2c_periph_reset()` を呼びます。LP ポートでは `lp_i2c_ll_reset_register()`（`:1583-1587`）で、戻り値がないため失敗が伝わりません。本文の説明と一致します。
- LP ポートのパッドは `init()` の `i2c_new_master_bus()`（`:2278-2300`、`lp_source_clk` は `:2283`）が LP IO 側に接続し、`beginTransaction()` は LP で `set_pin()` を呼びません（`:2555-2562`）。よって `i2c_stop()` の GPIO 操作はパッドに届きません。
- read の終端は `endTransaction()`（`:2620`）→ `i2c_wait(port, true)` で、`state == state_read` のため必ず強制 STOP 経路です（`:1988`）。write の終端は同じ分岐の else 側でコントローラの STOP を通るので（`:2000-2037`）、影響を受けません。本文の「write は無関係」と一致します。
- NACK のときはコントローラ自身の STOP を待って `i2c_stop()` を呼ばない、という記述も `hw_stopped` の判定（`:1952-1980`、`:1995-1998`）と一致します。
- 変更後は LP の read だけが else 側に入り、`STOP` + `END` を組んで `trans_start`、`TRANS_COMPLETE` / `TIMEOUT` を最大 25 ms 待ちます（`:2002-2011`）。完了しない場合は `connection_lost` にして `i2c_stop()` に落ちます（`:2016-2023`）。この経路は HP の write 終端で既に使われているものです。
- `LGFX_LP_I2C_NUM == 0`（IDF 5.4 未満、または LP I2C を持たないチップ）では `isLpPort()` が常に false なので、条件式は従来と同一に展開されます。既存ターゲットへの退行はありません。
- 補足として、C5 の 100/100 は「この経路で `END_DETECT` が毎回立ち、STOP が 25 ms 以内に完了している」ことの間接証拠でもあります。`!int_raw.end_detect` で強制 STOP 側に落ちていれば STOP はバスに出ず、次の read が失敗するはずです。

## 確認したいこと

1. **C5 以外の LP I2C チップ**。本文にあるとおり C6 / P4 も同じ `isLpPort()` の経路を通ります。C5 では read→read が 100/100 ですが、C6 / P4 の LP I2C でも「read 完了後に STOP コマンドだけを別の命令列で発行」が通るかは未確認です。もし通らない場合、この変更は「STOP が出ないまま成功する」から「read のたびに 25 ms 待って `connection_lost` を返す」に変わるため、退行の度合いが大きくなります。C6 か P4 のどちらかで read→read を 1 回確認できませんか。難しければ「C5 のみ実測」と明記したうえでマージし、他チップで問題が出たら追跡する、という判断でもよいと思います（最終的には maintainer の判断です）。

## 残る作業（本文の「別作業」と一致）

- LP では `i2c_stop()` が届かない経路が残ります：`beginTransaction()` の bus busy 復旧（`:2545-2549`）と `readBytes()` のタイムアウト（`:2754`）。エラー時に STOP がバスに出ないままペリフェラルがリセットされます。追跡用の issue を作っていただけると助かります。

## 未カバー（当方）

- hardware validation: NOT RUN（当方のテストセンターのノードに ESP32-C5 がありません）
- virtual-device validation: NOT RUN（C6 のプロファイルはありますが、QEMU の C6 LP ドメインは RTC_I2C 領域を all-ones で返すスタブのみで、LP I2C コントローラ自体が未実装です。C5 のプロファイルと ST25R3916 のモデルもありません）
- build / C6・P4 実機 / SDA・SCL 波形: NOT RUN

## 仮想デバイスで検証していない理由

当方の C6 仮想デバイスは LP I2C コントローラをモデル化しておらず（LP ドメインの RTC_I2C は読み出し all-ones のスタブ）、バスの STOP の有無を観測できません。C5 のプロファイルと ST25R3916（UnitNFC）のモデルもないため、virtual-device validation は実行していません。
