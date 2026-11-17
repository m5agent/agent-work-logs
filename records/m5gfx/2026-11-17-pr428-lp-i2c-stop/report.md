# M5GFX #428 レビュー報告：LP ポートの `i2c_stop()` でパッドを借りてバスを解放する

## 1. 背景

`M5GFX` の `i2c_stop()` は、SDA / SCL を通常の GPIO として操作し、9 クロック + STOP でバスを
解放する。ところが LP (低消費電力) I2C ポートのパッドは LP IO ドメインに接続されているため、
この操作はバスに出ず、エラー時の復旧も `init()` の初回バス解放も、コントローラのリセットだけに
なっていた（#426）。

#426 でこちらは、5 つの呼び出し経路（`i2c_wait()` の強制 STOP、STOP 未完了時の復旧、`init()` の
初回復旧、`beginTransaction()` の bus busy、`readBytes()` のタイムアウト）がすべてコード上で
バスに届かないことを code-level で確認し、案として「パッドを通常 GPIO に借りてから 9 クロック +
STOP を出し、ESP-IDF と同じ手順で LP 側に戻す」を提示した。同時に、著者が以前試して失敗した版は
戻すときの方向とプルの設定が欠けていたこと、`init()` の `initialized` 前の経路（経路 3）も
対象にする必要があること、コントローラのリセットはパッド返却より先に済ませること、復帰手順は
`init()` の LP 分岐と共通化するのがよいこと、を伝えた。

本 PR はその実装である。

## 2. 変更内容

1 file, +63/-0（`src/lgfx/v1/platforms/esp32/common.inl`）。

- `lp_pads_return(i2c_port, sda, scl)`（`:1857-1881`）：借りたパッドを LP I2C に戻す。
  `rtc_gpio_init(scl)` → SDA / SCL を `INPUT_OUTPUT_OD` → `pulldown_dis` → `pullup_en` →
  ラッチ High → `rtc_gpio_init(sda)` → 信号のつなぎ直し（P4 は `lp_gpio_connect_*_signal()`、
  C5 / C6 は `rtc_gpio_iomux_func_sel()`）。マクロ `LGFX_LP_I2C_LEND_PADS` は
  `LGFX_LP_I2C_NUM > 0 && SOC_RTCIO_INPUT_OUTPUT_SUPPORTED` で定義。
- `i2c_stop()`（`:1892-1903`, `:1931-1933`）：LP ポートが開いている（`i2c_bus_handle != nullptr`）
  ときは `release_lp_pad()` + `pinMode(input_pullup)` でパッドを通常 GPIO に借り、既存の
  9 クロック + STOP を実行。`i2c_periph_reset()`（`:1928`）とバックアップ復元（`:1930`）の後に
  `lp_pads_return()` を呼ぶ。
- `init()`（`:2311-2322`）：LP ポートなら常に `release_lp_pad()` + `pinMode()` してから
  `i2c_stop()`。`initialized` の前後で分岐しない。
- include（`:192-194`）：P4 用に `driver/lp_io.h`。

## 3. 確認したコード事実

### 3.1 #426 で指摘した 2 点

- 経路 3：`init()` の新しいブロックは `isLpPort()` だけで判定し、`initialized` を見ない。
  `i2c_port` が LP でなければ何もしない。したがって「前回の実行から LP 側のルーティングが残って
  いるが、まだ `initialized` が立っていない」状態でも、パッドを借りてからバス解放に入る。
- 順序：`i2c_stop()` の中では `i2c_periph_reset()` → `backup_pins.restore()` →
  `lp_pads_return()`。リセットがパッド返却より先。`lp_lent` の判定が `handle != nullptr` でも、
  `init()` 側は無条件に借りるので二重取得にはならない（`handle` が入るのは `init()` の
  `i2c_new_master_bus()` 成功後だけ）。

### 3.2 ESP-IDF v5.5.4 との照合

IDF の `s_lp_i2c_pins_config()`（`components/esp_driver_i2c/i2c_common.c`）は、SDA について
`rtc_gpio_init` → `rtc_gpio_set_direction(INPUT_OUTPUT_OD)` → `pulldown_dis` → `pullup_en` →
`rtc_gpio_iomux_func_sel` / `lp_gpio_connect_*` を行い、続けて SCL に同じことをする。
`lp_pads_return()` は同じ要素を、SCL のクロック有効化を先に、SDA の機能接続を最後に置く順序で
行っている。これは「SDA のラッチが High になる前に SDA を LP IO に戻すと偽の START になる」という
本文の説明と一致する。

IDF v5.5.4 の `rtc_gpio_init()` は `io_mux_enable_lp_io_clock()` と
`rtcio_hal_function_select(RTCIO_LL_FUNC_RTC)` だけで、方向・プル・ラッチには触れない。
`rtc_gpio_deinit()` は機能を digital に戻し、`SOC_LP_IO_CLOCK_IS_INDEPENDENT` のチップでは
ピン単位の LP IO クロックを force disable する。つまり `gpio::release_lp_pad()` が LP 側の接続を
外し、`rtc_gpio_init(sda)` を最後に置くことで、ラッチ High のまま LP 側へ戻せる。

### 3.3 `i2c_periph_signal[]` を LP ポート番号で引く点

PR は `i2c_periph_signal[i2c_port]` を LP のポート番号（C5 / C6 は 1、P4 は 2）で引く。IDF v5.5.4 では

- C5：`static_assert(SOC_I2C_NUM == SOC_HP_I2C_NUM + SOC_LP_I2C_NUM)`、LP エントリに
  `iomux_func = LP_I2C_MUX_FUNC`。
- C6：2 件目が LP エントリ（`iomux_func = LP_I2C_MUX_FUNC`）。
- P4：3 件目が LP エントリ（`LP_I2C_SDA_PAD_OUT_IDX` など）。

であり、範囲外参照にはならない。P4 は `SOC_LP_GPIO_MATRIX_SUPPORTED = 1`、C5 / C6 は未定義なので
分岐も正しい。`i2c_periph_signal` のサイズが LP を含むことは 5.4.2 でも同じ。

### 3.4 pull-up と `pinMode()`

`init()` は LP バスを `enable_internal_pullup = true`（`:2352`）で開くので、
`lp_pads_return()` が無条件に `rtc_gpio_pullup_en()` するのは既存の設定と整合する。
`pinMode()` は IO MUX を GPIO 機能に切り替え（RTC 独立でないチップでは RTC パッドの deinit と
プル設定も行う）、その後の LP 側の方向・プル・ラッチは `lp_pads_return()` が設定し直す。
`init()` の LP 分岐（`:2337-2342`）と同じ順序で、二重管理にはなっていない。

### 3.5 ビルド

PR のチェックは 26 行すべて pass。内訳は IDF 5.1.6 / 5.4.3 / 6.0.2 の esp32、c3、s3、
c5（5.5.2）、c6（5.4.3）、c61（5.5.2）、h2、p4（5.4.3）、pioarduino の c5 3.3.0 / c6 3.1.3 /
p4 3.1.3 / s3 / esp32、m5stack core、translation unit consistency。ビルドの確認であり、
実行時の挙動ではない。本文にある IDF 5.4.4 / 6.0.3 / 6.1 のネイティブビルドは CI の対象外で、
著者側の結果として引用する。

### 3.6 任意の改善

LP GPIO マトリクスの分岐（`:1869-1876`）は `#if SOC_LP_GPIO_MATRIX_SUPPORTED` だけで、
include 側の `__has_include(<driver/lp_io.h>)`（`:192-194`）と条件が揃っていない。将来ヘッダの
場所だけ変わってマクロが残るとビルドが壊れる。ブロッカーではない。

## 4. 検証方法と限界

- こちら側の証拠等級は **code-level verification**。PR head `0fdef4e` のソースと、ESP-IDF v5.5.4 の
  `i2c_common.c` / `rtc_io.c` / 各 SoC の `i2c_periph.c` を照合した。CI のビルド結果は補助证据。
- hardware validation は **NOT RUN**。ESP32-C5 実機がなく、ToughC5 + UnitNFC、Nesso N1、
  Tab5 の試験は再現していない。本文の表（3 ボードとも「借りない 0/0、借りる 100/100」、
  書き込み直後の最初の probe が Tab5 で 8/8）は著者の実機測定として引用する。
- virtual-device validation は **NOT RUN**。理由は具体的に、
  1. Device Service の 36 プロファイルに ESP32-C5 がない（C6 は `nanoc6` / `nesso-n1`、
     P4 は `tab5` だが `tab5_enabled = false`）。
  2. esp-emulator の QEMU ソース（C6 バックエンド）には LP I2C コントローラのモデルがなく、
     `hw/misc` にあるのは `esp32c6_i2c_ana_mst.c`（アナログマスタ）だけ。LP IO MUX / RTC IO の
     パッド配線もモデル化されていない。
  3. この変更の観測量は LP IO ドメインのパッド配線と、STOP がバスに出たかどうかであり、
     GPIO レベルのモデルでは原理的に再現できない。
  4. 本機に M5GFX をビルドできる Arduino / PlatformIO 環境がない（Arduino コア・pio とも未導入）。
- したがって、この PR の効果そのもの（実機で STOP がバスに出るか）は著者の測定に依存する。
  こちらが独立に確認できたのは「変更が意図どおりの順序・条件で呼ばれ、IDF の手順と一致し、
  ビルドが通る」ところまで。

## 5. 影響範囲

- 変更は LP I2C ポートを使うチップ（C5 / C6 / P4）の `i2c_stop()` と `init()` に限定。
  `LGFX_LP_I2C_NUM == 0` のチップ（S3、ESP32 など）ではマクロが定義されず、コードは
  コンパイルされない。
- HP ポートの `i2c_stop()` の挙動は変わらない（`lp_lent` が false）。
- `i2c_stop()` の呼び出しは 5 箇所のままで、追加の呼び出しはない。
- 失敗時の影響：`lp_pads_return()` の戻り値は無視されるが、`rtc_gpio_is_valid_gpio()` が false の
  ピンでは `init()` の `i2c_new_master_bus()` が失敗して LP ポートは開かないため、到達しない。

## 6. 未覆盖项

- わざとバスを止めた状態（SDA を Low に保持）からの復旧：`NOT RUN`。これが `i2c_stop()` の
  本来の用途であり、9 クロック + STOP と、戻した後に偽の START が出ないことの実機確認が残る。
- ESP-IDF 5.4 / 6.0 の実機、ESP-IDF 6.1 の C5 実機：`NOT RUN`（著者も未確認）。
- LP ポートを使う他ボード（ToughC5 以外の C5 ボード、C6 / P4 の他ボード）：`NOT RUN`。
- 実機の電気特性（立ち上がり、クロックストレッチ、UnitNFC 固有のタイミング）：対象外。
