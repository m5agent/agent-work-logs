## 結論

訂正を受け入れます。前回の「2 バイト書き込み + RSTART の分割」という見立ては撤回します。今回の説明はコードの分岐と一致しています。

- `i2c_wait()` は read 終端（`state == state_read`）を常に強制 STOP 側へ分岐します（`develop` `b48dce0`、`src/lgfx/v1/platforms/esp32/common.inl:1984-1998`）。
- `i2c_stop()` は `gpio_set_level()` / `gpio_set_direction()` だけで STOP を作り、IO MUX を GPIO に戻す `gpio_iomux_out(..., PIN_FUNC_GPIO)` を呼びません（`:1847-1882`。`set_pin()` は `:1774` で呼んでいます）。LP パッドが LP IO 機能のままなら、この操作はパッドに届きません。
- 終端の `i2c_periph_reset()` は LP では `lp_i2c_ll_reset_register()` を呼び、戻り値がないため成功扱いになります（`:1580-1592`）。
- write 終端は else 側でコントローラの STOP コマンドを通るので影響を受けない、という点も一致します。
- read が 1 バイト受けてバッファを上書きする点も、`readBytes()` が FIFO から読んだ分を書いてからタイムアウトを判定する実装（`:2749-2772`）と矛盾しません。

つまり「直前のトランザクションが read で終わったか」で次が壊れる、という条件はコード上の分岐とそのまま対応します。前回の `writeBytes()` の FIFO 未確認説も原因候補から外れます。

## 証拠等級

code-level verification（M5GFX `develop` `b48dce0`、ESP-IDF `v5.5` の ESP32-C5 側ソース）。当方の hardware validation / virtual-device validation は NOT RUN です。C5 実機がなく、仮想デバイス環境のプロファイルも C6 までで C5 がなく、QEMU にも LP_I2C / ST25R3916 のモデルがないためです。実機の裏付けは提示いただいた ToughC5 の測定が唯一です。

## 必要ステップ

1. develop の現状確認。修正 3 と同じ目的の処理（`i2c_new_master_bus()` 前のラッチ preset）は develop に既に入っています（`aef1da8`、2026-11-06、"i2c: keep SDA high while the LP port pads are configured"、`common.inl:2258-2277`）。6f81929 はこの前なので、そちらで見えた「begin 直後の最初のトランザクションが NACK」は最新 develop では出ない可能性が高いです。まず最新 develop で再確認してください。
2. develop HEAD への rebase。差分はそのままは当たりません。`git apply --check` では hunk 1〜3 はオフセット付きで通り、`i2c_wait()` の hunk は日本語コメントの英語化（`40928dd`）で一致しません。修正 3 で残るのは `init()` の `i2c_stop()` 前に `gpio::release_lp_pad()` を置く部分だけです（`gpio::release_lp_pad()` 自体は `:737` に既存）。なお `route_lp_pad()` の `i2c_periph_signal[i2c_port].iomux_func` は C5 で有効です。C5 は `SOC_LP_GPIO_MATRIX_SUPPORTED` を持たず、IDF v5.5 `soc/esp32c5/i2c_periph.c` に LP 用エントリ（`iomux_func = 3`）があることを確認しました。
3. 修正 1 単独の測定を 1 回お願いします。現状は「修正 2 だけ」と「両方」の結果で、修正 1 単独が未取得です。修正 1 が単独で通れば、通常の read 終端はコントローラ STOP で閉じられ、パッドの貸し出し（修正 2）はエラー復旧と init の bus-busy 経路だけに限定できます。
4. 回帰観点：100 kHz / 400 kHz、read→read、read→write、write→read、連続周回、NACK を強制した復旧（9 クロック + STOP）、`begin()` 直後の最初の 1 回。修正 2 は bus-busy 復旧でコントローラが動いたままパッドを外す順序なので、復旧系の確認を厚めにしてください（必要なら periph reset / `fsm_rst` で止めてから借りる順序も比較）。
5. まとまったら PR の形で出してください。C5 実機がこちらにないため、修正前 / 修正後 / 修正 1 単独 / 修正 2 単独のログを添えてもらえればコード側のレビューを返します。

## 未カバー項目

- 当方での C5 実機再現、SDA/SCL 波形、LP_I2C レジスタダンプ：NOT RUN
- パッチのビルド・実機検証：NOT RUN（そちらの環境のみ）
- 修正 1 単独の結果、NACK 復旧の実機確認：未取得
- 仮想デバイスでの再現：不可（C5 プロファイル / LP_I2C モデルなし）
