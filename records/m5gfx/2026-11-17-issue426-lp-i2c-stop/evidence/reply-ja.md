# 返信本文（日本語・1 条）

> 投稿先: https://github.com/m5stack/M5GFX/issues/426
> 投稿済み: https://github.com/m5stack/M5GFX/issues/426#issuecomment-6935810184
> 状態: Issue は OPEN のまま。コード変更・push なし。

---

ご報告の 5 経路と機構は `develop` `b48dce0` のコードと一致しています。LP ポートでは、コード上 `i2c_stop()` はバスに何も送出せず、LP I2C コントローラのリセットだけが起きます。

**証拠の等級: code-level verification**（`b48dce0` と ESP-IDF v5.5 のソース照合）。hardware validation / virtual-device validation は NOT RUN です。

仮想デバイスで検証していない理由：本機の Device Service 36 profile に ESP32-C5 がなく、esp-emulator にも C5 の QEMU 機がありません。C6 / P4 を含めて LP I2C コントローラ自体が未モデル化で、この不具合は LP IO ドメインのパッドのルーティングに依存するため、GPIO レベルのモデルでは再現できません。

### 確認したコード事実

- `i2c_stop()` の呼び出しは 5 箇所だけで、表と一致します：`common.inl:1997`（`i2c_wait()` の強制 STOP）、`:2022`（STOP 未完了時の復旧）、`:2255`（`init()` の初回復旧）、`:2548`（`beginTransaction()` の bus busy）、`:2754`（`readBytes()` のタイムアウト）。他に呼び出しはありません。
- `i2c_stop()` 本体（`:1847-1882`）は `gpio_set_level` / `gpio_set_direction` / `gpio_get_level` と `pin_backup_t` だけを使います。IDF v5.5 の `gpio_set_direction()` は input / output / open-drain の enable を操作するだけで、IO MUX の関数選択（mcu_sel）を切り替えません（`components/esp_driver_gpio/src/gpio.c:306-336`）。LP パッドの関数選択は IDF が `rtc_gpio_iomux_func_sel()` で行っており（`components/esp_driver_i2c/i2c_common.c:355-399`）、`i2c_stop()` はこの経路を通りません。
- C5 では `LGFX_GPIO_RTC_INDEPENDENT`（= `SOC_GPIO_SUPPORT_RTC_INDEPENDENT`）が 1 なので、`pin_backup_t` は RTC / LP 側のレジスタを保存・復元しません（`common.inl:783`, `:836`）。`i2c_stop()` の `pin_backup_t` による復元も LP 側には及びません。
- 最後の `i2c_periph_reset()` は LP では `lp_i2c_ll_reset_register()` だけです（`common.inl:1582-1590`）。IDF v5.5 の実装は `LPPERI.reset_en.lp_ext_i2c_reset_en` を 1 パルスするだけで、戻り値も `void` です（`components/hal/esp32c5/include/hal/i2c_ll.h:875-882`）。バスには何も出ず、失敗も呼び出し側に伝わりません。
- `b48dce0` では read 終端も `state == state_read` で強制 STOP 側に入るため、#423 がマージされるまでは正常な read でも `:1997` を通ります。#423 後も、表に挙げられたエラー / タイムアウト / 復旧の経路は残ります。

### 案 2（コントローラの bus clear + STOP）について

C5 の **LP I2C** レジスタブロックには bus clear 用の `scl_sp_conf`（`scl_rst_slv_en` / `scl_rst_slv_num`）と `ctr.conf_upgate` があります（IDF v5.5 `components/soc/esp32c5/register/soc/lp_i2c_struct.h:224`, `:352-380`, `:869`）。`i2c_ll_master_clr_bus()` / `i2c_ll_master_is_bus_clear_done()` も同じヘッダにあります（`components/hal/esp32c5/include/hal/i2c_ll.h:755-795`）。

ただし C5 の `soc_caps.h` には `SOC_I2C_SUPPORT_HW_CLR_BUS` がありません（S3 / C6 / P4 にはあります）。そのため IDF 自身の `i2c_master_bus_reset()` は C5 では GPIO のビット操作経路を選びます（`components/esp_driver_i2c/i2c_master.c:60-104`）。コード上は LP ポートでもこれが同じ理由でパッドに届かないため、IDF は参考実装になりません。LP インスタンスが実際に 9 クロックを出すかは実機で確認が必要です（こちらでは NOT RUN）。

### 案 1（パッドを借りて戻す）について

IDF の LP ピン設定は、SDA / SCL それぞれについて `rtc_gpio_init` → `rtc_gpio_set_direction(INPUT_OUTPUT_OD)` → `rtc_gpio_pulldown_dis` → `rtc_gpio_pullup_en` → `rtc_gpio_iomux_func_sel(..., i2c_periph_signal[port].iomux_func)` の順です（`i2c_common.c:355-399`）。また `rtc_gpio_deinit()`（`gpio::release_lp_pad()` が使用）は `SOC_LP_IO_CLOCK_IS_INDEPENDENT` のチップでピン単位の LP IO クロックを force disable し、`rtc_gpio_init()` が再度 enable します（`components/esp_driver_gpio/src/rtc_io.c:44-73`、C5 は `soc_caps.h:221`）。

`M5.begin()` の PM1 設定で失敗した版が、このうち direction と pull の設定を落としていないか確認したいです。こちらでは失敗原因を特定できていません（未確定）。

### 未カバー

- hardware validation: NOT RUN。ESP32-C5 実機がなく、SDA / SCL のオシロ観測も未実施です。
- virtual-device validation: NOT RUN。C5 profile なし、LP I2C コントローラ未モデル化。
- 案 1 / 案 2 の成立可否: NOT RUN。コード上の候補整理のみで、パッチ・ビルド・実機はいずれも未実施です。
- C6 / P4 など他の LP I2C チップ: NOT RUN。

コードは変更していません。参照箇所と IDF の摘録はこちらに置きました: <record-url>
