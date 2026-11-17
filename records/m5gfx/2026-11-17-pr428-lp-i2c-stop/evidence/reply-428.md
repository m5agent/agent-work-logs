`init()` の経路 3 と、パッドを戻す順序の 2 点は、この変更で解消されていることを確認しました。ブロッカーは見つかりませんでした。

**証拠の等級: code-level verification**（PR head `0fdef4e` と ESP-IDF v5.5.4 のソース照合、およびこの PR の CI ビルド結果）。hardware validation は本文の表（作者側の測定）で、こちらでは再測していません。virtual-device validation は NOT RUN です。

## 確認したコード事実

- 経路 3（`initialized` が立つ前の `init()`）は、LP ポートなら常に `release_lp_pad()` + `pinMode()` でパッドを借りてから `i2c_stop()` を呼ぶ形になっています（`common.inl:2311-2322`）。`initialized` の前後で分岐しないので、前回の実行から残った LP 側の接続もここで外れます。
- 戻す順序は、`i2c_periph_reset()`（`:1928`）→ `pin_backup_t` の復元（`:1930`）→ `lp_pads_return()`（`:1931-1933`）で、コントローラのリセットがパッドの返却より先に済んでいます。借りる判定が `i2c_bus_handle != nullptr`（`:1893`）でも、`init()` 側は常時借りるので二重には借りません。
- `lp_pads_return()`（`:1857-1881`）は IDF v5.5.4 の `s_lp_i2c_pins_config()` と同じ手順です。`rtc_gpio_init()` は LP IO クロックの有効化と機能選択だけで、方向・プル・出力ラッチには触れません（`rtc_io.c` の `rtc_gpio_init`）。したがって「SDA のラッチを High にしてから `rtc_gpio_init(sda)`」の順序で偽の START が出ない、という本文の説明と一致します。`rtc_gpio_deinit()` が機能を digital に戻すことも確認しました。
- `i2c_periph_signal[i2c_port]` を LP のポート番号で引く点が今回の新しい依存ですが、C5 は `static_assert(SOC_I2C_NUM == SOC_HP_I2C_NUM + SOC_LP_I2C_NUM)` があり、C6 は 2 件目、P4 は 3 件目に LP の `iomux_func` / `sda_out_sig` があります（IDF v5.5.4 の各 `soc/<chip>/i2c_periph.c`）。範囲外参照にはなりません。
- `pinMode()` が IO MUX を GPIO 機能に切り替えた後、LP 側の方向・プル・ラッチは `lp_pads_return()` が設定し直し、`init()` の LP 分岐（`:2337-2342`）と同じ順序です。`init()` は `enable_internal_pullup = true`（`:2352`）で開くので、無条件の `rtc_gpio_pullup_en()` とも整合しています。
- CI は c5（IDF 5.5.2）、c6 / p4（IDF 5.4.3）、pioarduino の c5 3.3.0 / c6 3.1.3 / p4 3.1.3 を含めて全 pass です（ビルドのみで、実行時の挙動ではありません）。

## 未カバー

- わざとバスを止めた状態からの復旧は、本文どおり NOT RUN です。ここが `i2c_stop()` の本来の用途なので、SDA を 1kΩ で GND に落とすか別 GPIO の open drain で保持し、エラー後の `i2c_stop()` で 9 クロック + STOP が出て、戻した後に偽の START が出ないことを 1 回見ていただけると、経路 1 / 2 / 5 が閉じます。
- こちら側の hardware validation は NOT RUN（ESP32-C5 実機なし）。virtual-device validation も NOT RUN です。Device Service に C5 プロファイルがなく、C6 / P4 の QEMU バックエンドには LP I2C コントローラも LP IO MUX / RTC IO のパッドモデルもありません（`hw/misc` にあるのは `esp32c6_i2c_ana_mst.c` のみ）。この変更は LP IO ドメインのパッド配線に依存するため、GPIO レベルのモデルでは再現できません。
- ESP-IDF 5.4 / 6.0 の実機、ESP-IDF 6.1 の C5 実機は、本文どおり未確認です。

## 任意（ブロッカーではありません）

LP GPIO マトリクスの分岐（`:1869-1876`）が `SOC_LP_GPIO_MATRIX_SUPPORTED` だけで、`driver/lp_io.h` の有無（`:192-194`）を見ていません。将来ヘッダの場所だけ変わってマクロが残るとビルドが壊れるので、include と同じ `__has_include` を条件に加えておくと安全だと思います。

参照したコードと IDF の摘録はこちらに置きました: PLACEHOLDER_RECORD_URL
