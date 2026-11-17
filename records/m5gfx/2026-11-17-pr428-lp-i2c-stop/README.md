# M5GFX #428: LP ポートでも `i2c_stop()` のバス解放をピンに届かせる（レビュー）

- 日期：`2026-11-17`
- 结果：`PARTIAL`（code-level verification と CI ビルドは確認。hardware / virtual-device は `NOT RUN`）
- 工作类型：`pr`
- 条目：[m5stack/M5GFX#428](https://github.com/m5stack/M5GFX/pull/428)
  「i2c: LP ポートでも i2c_stop() のバス解放をピンに届かせる」，作者 GOB52，日文，OPEN，レビュー・コメント 0 件（取得時）
- 源码：PR head `0fdef4e88d98eb4b754bea6d993244b2331f231a`，base `develop` `21213080fba00c675d5dcca0ef2abd4b349e3cef`
- 环境：macOS、ESP-IDF v5.5.4 のローカルソース木、Device Service 36 プロファイル、esp-emulator の QEMU ソース

## 结论

1. #426 で指摘した 2 点は、どちらもこの変更で解消されている。
   (a) `init()` の経路 3（`initialized` が立つ前）は、LP ポートなら常に `release_lp_pad()` + `pinMode()` で
   パッドを借りてから `i2c_stop()` を呼ぶ（`common.inl:2311-2322`）ため、前回の実行から残った LP 側の
   接続も外れる。(b) コントローラのリセット（`:1928`）→ バックアップ復元（`:1930`）→
   `lp_pads_return()`（`:1931-1933`）の順で、リセットがパッド返却より先に済んでいる。
2. `lp_pads_return()`（`:1857-1881`）は ESP-IDF v5.5.4 の `s_lp_i2c_pins_config()` と同じ順序
   （`rtc_gpio_init` → 方向 OD → `pulldown_dis` → `pullup_en` → 出力ラッチ High）で、SDA を最後に
   LP 側へ戻す。`rtc_gpio_init()` は LP IO クロックの有効化と機能選択だけで方向・プル・ラッチに
   触れないため、この順序で偽の START が出ないという本文の説明と整合する。
3. LP ポート番号で `i2c_periph_signal[]` を引く新しい依存は範囲外参照にならない。C5 は
   `static_assert(SOC_I2C_NUM == SOC_HP_I2C_NUM + SOC_LP_I2C_NUM)`、C6 は 2 件目、P4 は 3 件目に
   LP の `iomux_func` / `sda_out_sig` がある（IDF v5.5.4）。
4. CI は c5（IDF 5.5.2）、c6 / p4（IDF 5.4.3）、pioarduino の c5 3.3.0 / c6 3.1.3 / p4 3.1.3 を
   含めて全 pass（ビルドのみ。実行時の挙動ではない）。
5. ブロッカーなし。唯一残るのは、PR 本文自身が未確認としている「わざとバスを止めた状態からの復旧」
   （SDA を Low に保持した状態で 9 クロック + STOP が出るか）で、これは `i2c_stop()` の本来の用途。
6. 任意の改善として、`lp_gpio_*` 分岐（`:1869-1876`）の条件が `SOC_LP_GPIO_MATRIX_SUPPORTED` だけで
   `driver/lp_io.h` の有無（`:192-194`）を見ていない点を挙げた。ブロッカーではない。

## 关键证据

- `evidence/pr-428.diff`：PR の全差分（1 file, +63/-0）。
- `evidence/source-lines.txt`：PR head の include ガード、`lp_pads_return()`、`i2c_stop()`、
  `init()` の LP 分岐。
- `evidence/idf5554-lp-pin-setup.txt`：ESP-IDF v5.5.4 の `s_lp_i2c_pins_config()` と
  `rtc_gpio_init()` / `rtc_gpio_deinit()`。
- `evidence/idf5554-i2c-periph-lp.txt`：C5 / C6 / P4 の `i2c_periph_signal[]` の LP エントリ。
- `evidence/ci-checks.txt`：PR のチェック一覧（全 pass、26 行）。
- `evidence/platform-coverage.txt`：Device Service の SoC 一覧（C5 なし）と、QEMU 側に LP I2C /
  LP IO のモデルがないこと。
- `evidence/reply-428.md` / `evidence/reply-posted.txt`：投稿した日本語返信と投稿結果。
- 已发布回复：<https://github.com/m5stack/M5GFX/pull/428#issuecomment-6942651614>（1 条，日本語。PR は OPEN のまま、close / push なし）

## 文件

- `report.md`：機序、コード位置、検証方法、影響範囲、未覆盖项
- `run.json`：構造化状態
- `evidence/`：差分、ソース抜粋、IDF 摘録、CI、環境の網羅状況、返信

## 未覆盖项

- hardware validation：`NOT RUN`。ESP32-C5 実機がなく、ToughC5 / Nesso N1 / Tab5 の
  UnitNFC (ST25R3916) 試験は再現していない。本文の表（3 ボードとも 0/0 → 100/100）は
  作者の実機測定として引用する。
- virtual-device validation：`NOT RUN`。Device Service に C5 プロファイルがなく、C6 / P4 の
  QEMU バックエンドには LP I2C コントローラも LP IO MUX / RTC IO のパッドモデルもない。
  この変更は LP IO ドメインのパッド配線に依存するため、GPIO レベルのモデルでは再現できない。
- わざとバスを止めた状態（SDA を Low に保持）からの復旧：`NOT RUN`（作者も未実施）。
- ESP-IDF 5.4 / 6.0 の実機、ESP-IDF 6.1 の C5 実機：`NOT RUN`（作者も未確認）。
- 本機に M5GFX をビルドできる Arduino / PlatformIO 環境がないため、独自ビルドはしていない
  （ビルドは CI の結果を引用）。
