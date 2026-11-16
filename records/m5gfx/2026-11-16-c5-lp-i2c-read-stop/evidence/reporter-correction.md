## 訂正: 本文の切り口は誤りでした

本文では「2 バイト書き込み + repeated start の組み合わせが失敗する」と書きましたが、これは誤りでした。ToughC5 の実機で切り分け直した結果、原因は次のとおりです。

**LP_I2C ポートでは、read で終わるトランザクションの後に STOP がバスに出ていません。**

そのため、read で終わったトランザクションの**次の** 1 トランザクション (read でも write でも) を、デバイスが直前の状態のまま解釈します。write で終わるトランザクションは、コントローラ自身の STOP コマンドで閉じるので影響を受けません。失敗の条件は「失敗した転送の形」ではなく、「直前のトランザクションが read で終わったかどうか」です。

本文の再現で失敗に見えたのは、ST25R3916 の「Space B へのアクセスは STOP を受けるまで続く」という仕様のためです。Space B を read した後に STOP が出ないので、チップは Space B のまま次のフレームを受け取り、続く read / write の解釈がずれていました。

また、本文の「read はバッファに手を触れない」も誤りでした。番兵の `0xEE` は `0x00` で上書きされており、read 自体は 1 バイト受け取っています。

## 原因 (コード)

`src/lgfx/v1/platforms/esp32/common.inl` の `i2c_wait()` は、read で終わったトランザクションを `endTransaction()` で閉じるとき、必ず `i2c_stop()` を通ります (強制 STOP 経路)。`i2c_stop()` は SDA/SCL を通常の GPIO で操作して STOP を作ります。

LP ポートのピンは、ESP-IDF の `i2c_new_master_bus()` が LP IO 側に接続しています。そのため、通常の GPIO を操作してもピンは動かず、STOP が出ません。`i2c_stop()` の最後にある `i2c_periph_reset()` で LP_I2C はリセットされるので、呼び出しはすべて成功を返します。

## 実測 (ToughC5 + UnitNFC、修正前の M5GFX)

| 手順 | 結果 |
|---|---|
| Space B `0x0C` を read (2 バイト選択 `0xFB, 0x4C` → repeated start → read) | `0x93` (データシートの既定値どおり) |
| Space A `0x0C` を read | `0x2D` (Space B とは別の値) |
| Space B の read の直後に Space A `0x0C` を read | **`0xFF`** |
| Space B の read の後に、write だけのトランザクション (start + stop) を挟んでから Space A `0x0C` を read | `0x2D` |
| write だけのトランザクションを挟んでから、Space B `0x0F` に 2 バイト選択で書き、読み戻す | 一致 |

## ご依頼の切り分けへの回答

1 と 2 は、修正前の M5GFX (develop `6f81929`。read の後を強制 STOP 経路で閉じる条件は 0.3.0 `28d4794` と同一) で、ご指定どおりの条件で測りました。各測定の直前に write だけのトランザクション (start + stop) を入れ、直前の read の STOP 欠落が混ざらないようにしています。6 周回とも同じ結果でした。

| 書き方 | Space B `0x0C` (既定値 `0x93`) |
|---|---|
| 対照: Space A `0x0C` を 1 バイト選択で read | `0x2D` (正しい) |
| baseline: `write(sel, 2)` → `restart()` → `read()` | `0x93` (正しい) |
| 1. `write(&b0, 1); write(&b1, 1);` → `restart()` → `read()` | `0x93` (正しい) |
| 2. `write(sel, 2); delayMicroseconds(100);` → `restart()` → `read()` | `0x93` (正しい) |

3 通りとも正しく読めます。2 バイト書き込み + repeated start の経路そのものに失敗はなく、1 と 2 で切り分ける対象の失敗は存在しませんでした。

3. **ESP-IDF の `i2c_master_transmit_receive()` で同じ転送を実行:** 実施していません。下記の修正案 (LP ポートでは read の後もコントローラの STOP を使う) を当てると、本文の再現スケッチが Core (HP I2C) と同じ結果になったため、原因は M5GFX 側と判断しました。

**`0xFF` の件 (リセット直後の最初のトランザクション):** 引き金はアイドルではなく「直前のトランザクションが read で終わったこと」です。各周回の最初の Space A の read の直前は、前の周回の Space B の read でした。

## 同じ原因による影響: `i2c_stop()` のバス復旧

`i2c_stop()` は、エラー時のバス復旧 (9 クロック + STOP) にも使われています。こちらも同じ理由でピンに届かないので、LP ポートではバス復旧も効いていません。

## 関連する別の問題: LP ポートを開き直した直後の最初のトランザクション

原因は本件と別ですが、LP ポートに固有で、本文の再現スケッチにも影響するので併記します。

`M5.Ex_I2C.begin()` などで LP ポートを開き直すと、直後の最初のトランザクションがアドレス NACK で毎回失敗します。ESP-IDF の `i2c_new_master_bus()` は LP ピンの設定の途中で、LP GPIO の出力ラッチが 0 のまま出力を有効にします。このとき線が一瞬 Low に引かれ、偽の START が出ていました。出力ラッチを事前に High にしておくと、最初のトランザクションも成功しました (リセット 4 回とも)。

本文の再現スケッチは `setup()` で `M5.Ex_I2C.begin()` を呼ぶので、最初の周回の最初のトランザクションがこの影響を受けます。

## 修正案 (`common.inl` のみ、参考)

こちらで考慮できていない前提や設計上の約束があるかもしれないので、PR ではなくコードの提示に留めます。develop `6f81929` に対する差分です。

本件の修正は次の 2 つです。

1. `i2c_wait()`: LP ポートでは、read で終わったトランザクションも `i2c_stop()` を通さず、コントローラの STOP コマンドで閉じます。HP ポートの動作は変えていません。
2. `i2c_stop()`: LP ポートが開いているときは、復旧の間だけピンを通常の GPIO に戻し、終わったら LP の I2C 機能に戻します。エラー時のバス復旧のように、1 では避けられない経路もこれで効きます。1 を外して 2 だけにした状態 (read を `i2c_stop()` で閉じる旧経路) でも STOP がバスに届き、本件の症状は出ませんでした。

関連する別の問題の修正は次の 1 つです。

3. `init()` (LP ポート): 前回の実行から残っている LP 側の接続を外してからバス復旧を行い、`i2c_new_master_bus()` の前に出力ラッチを High にします。

<details>
<summary>差分</summary>

```diff
diff --git a/src/lgfx/v1/platforms/esp32/common.inl b/src/lgfx/v1/platforms/esp32/common.inl
index 74bfa1b..d6cc171 100644
--- a/src/lgfx/v1/platforms/esp32/common.inl
+++ b/src/lgfx/v1/platforms/esp32/common.inl
@@ -1742,6 +1742,29 @@ namespace lgfx
 #endif
     }
 
+#if LGFX_LP_I2C_NUM > 0 && SOC_RTCIO_PIN_COUNT > 0
+    /// Sets the output latch of a low power pad high. While the pad is being routed it
+    /// passes through the low power GPIO function with its output enabled, where a low
+    /// latch pulls the line down and the devices on the bus see a false START.
+    static void preset_lp_pad(const gpio_num_t pin)
+    {
+      rtc_gpio_set_level(pin, 1);
+    }
+
+    /// Routes a pad borrowed by i2c_stop() back to the low power controller. Direction and
+    /// pulls stay in the low power IO registers, which the borrowing does not touch.
+    static void route_lp_pad(const int i2c_port, const gpio_num_t pin)
+    {
+      preset_lp_pad(pin);
+      rtc_gpio_init(pin);
+ #if !SOC_LP_GPIO_MATRIX_SUPPORTED
+      rtc_gpio_iomux_func_sel(pin, i2c_periph_signal[i2c_port].iomux_func);
+ #else
+      (void)i2c_port;  // the low power GPIO matrix keeps its routing
+ #endif
+    }
+#endif
+
     static void i2c_stop(int i2c_port)
     {
       static constexpr int I2C_CLR_BUS_HALF_PERIOD_US = 2;
@@ -1751,6 +1774,17 @@ namespace lgfx
       gpio_num_t scl_io = i2c_context[i2c_port].pin_scl;
       gpio::pin_backup_t backup_pins[] = { sda_io, scl_io };
 
+#if LGFX_LP_I2C_NUM > 0 && SOC_RTCIO_PIN_COUNT > 0
+      // The pads of an open low power port are routed through the low power IO domain,
+      // out of reach of the GPIO writes below: lend them to the normal GPIO meanwhile.
+      const bool lp_routed = isLpPort(i2c_port) && (i2c_context[i2c_port].i2c_bus_handle != nullptr);
+      if (lp_routed)
+      {
+        pinMode(sda_io, pin_mode_t::input_pullup);  // also releases the low power routing
+        pinMode(scl_io, pin_mode_t::input_pullup);
+      }
+#endif
+
       gpio_set_level(sda_io, 1);
       gpio_set_direction(sda_io, GPIO_MODE_INPUT_OUTPUT_OD);
 
@@ -1777,6 +1811,13 @@ namespace lgfx
       i2c_periph_reset(i2c_port);
 #endif
       for (auto &bup : backup_pins) { bup.restore(); }
+#if LGFX_LP_I2C_NUM > 0 && SOC_RTCIO_PIN_COUNT > 0
+      if (lp_routed)
+      {
+        route_lp_pad(i2c_port, sda_io);
+        route_lp_pad(i2c_port, scl_io);
+      }
+#endif
     }
 
     /// Minimum time a transfer may stall (clock stretching or a wedged bus)
@@ -1879,11 +1920,15 @@ namespace lgfx
 
       if (flg_stop || res.has_error())
       {
+        // A read is normally closed by i2c_stop(), which drives the pins through the GPIO
+        // matrix. The pads of a low power port are routed through the low power IO domain
+        // instead, where that STOP never reaches the bus, so the controller sends it there.
+        const bool force_stop_read = (i2c_context[i2c_port].state == i2c_context_t::state_read) && !isLpPort(i2c_port);
 #if LGFX_I2C_REG_LAYOUT == 3
 // エラー発生後はペリフェラルが強制停止済みの場合があり、通常のSTOPコマンド発行では完了割り込みが来ずタイムアウトまで待たされるため強制STOP側へ分岐する;
-        if (res.has_error() || i2c_context[i2c_port].state.has_error() || i2c_context[i2c_port].state == i2c_context_t::state_read || !int_raw.end_detect_int_raw)
+        if (res.has_error() || i2c_context[i2c_port].state.has_error() || force_stop_read || !int_raw.end_detect_int_raw)
 #else
-        if (res.has_error() || i2c_context[i2c_port].state.has_error() || i2c_context[i2c_port].state == i2c_context_t::state_read || !int_raw.end_detect)
+        if (res.has_error() || i2c_context[i2c_port].state.has_error() || force_stop_read || !int_raw.end_detect)
 #endif
         { // force stop
           // state が既にエラーの場合はエラー検出箇所で停止済みのため再停止しない (res のエラーはこの呼び出しで検出されたもので未停止);
@@ -2151,11 +2196,23 @@ namespace lgfx
         return {};
       }
 
+#if LGFX_LP_I2C_NUM > 0 && SOC_RTCIO_PIN_COUNT > 0
+      if (isLpPort(i2c_port))
+      { // Routing left by a previous run survives a reset and would keep the bus clearing
+        // below off the pads. (see gpio::release_lp_pad)
+        gpio::release_lp_pad(pin_sda);
+        gpio::release_lp_pad(pin_scl);
+      }
+#endif
       i2c_stop(i2c_port);
 
 #if LGFX_LP_I2C_NUM > 0
       if (isLpPort(i2c_port))
       {
+ #if SOC_RTCIO_PIN_COUNT > 0
+        preset_lp_pad(pin_sda);
+        preset_lp_pad(pin_scl);
+ #endif
         i2c_master_bus_config_t bus_config;
         memset(&bus_config, 0, sizeof(i2c_master_bus_config_t));
         bus_config.i2c_port = i2c_port;
```

</details>

## 修正案を当てた状態での検証 (ToughC5 + UnitNFC)

- 本文の再現スケッチ: `the mark is in space B: the two byte selection works` (Core と同じ)。
- Space B の read の直後の Space A の read: `0x2D` (修正前は `0xFF`)。
- 修正 2 だけの状態 (read を `i2c_stop()` で閉じる旧経路にわざと戻した状態) でも、STOP がバスに届き、後続の転送が正常。
- `M5.Ex_I2C.begin()` 直後の 1 回目のトランザクション (修正 3): リセット 4 回とも成功 (修正前は毎回失敗)。

