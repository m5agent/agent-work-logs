# M5GFX #424 报告：`release_held_sda()` が途中の 1 ビットで STOP を打ち切る

## 1. 問題と背景

- 対象：[m5stack/M5GFX#424](https://github.com/m5stack/M5GFX/issues/424)（作者 GOB52）
- 基線：`develop` `b48dce04c80d3e3c9874b7ba946c43d672129c28`、M5GFX 0.3.0 も同区間は同一
  （`probe_hardware.inl:13-44` の MD5 が一致）
- 現象：ToughC5（ESP32-C5）で、UnitNFC（ST25R3916、`0x50`）を read している最中にホストから
  RTS でハードリセットすると、一定割合で `M5.getBoard()` が `0x00` になる。LP I2C ポートが
  割り当てられず `M5.Ex_I2C.getPort()` が `-1` になる。
- 作者の切り分け：LP 側の pin mux と LP I2C コントローラの状態は CPU リセットで消えない。
  `probe_i2c_bus_present()` に入る時点では SCL High / SDA Low で、`release_held_sda()` が
  `false` を返すためボード判定から外れる。PR #423 で read が正常化するとこの状態が起きやすい。

## 2. コード上の機序

`src/board_detect/probe_hardware.inl`

```text
15  bool release_held_sda(int pin_sda, int pin_scl)
...
24    bool bus_released = io::pin_read(pin_scl);
25    if (bus_released && !io::pin_read(pin_sda))
26    {
27      for (int i = 0; i < 9 && !io::pin_read(pin_sda); ++i)
28      {
29        io::pin_low(pin_scl);
30        io::delay_us(5);
31        if (!wait_i2c_scl_high(pin_scl)) { bus_released = false; break; }
32      }
33      if (bus_released)
34      {
35        io::pin_low(pin_scl);
36        io::pin_low(pin_sda);
37        io::delay_us(5);
38        bus_released = wait_i2c_scl_high(pin_scl);
39        if (bus_released)
40        {
41          io::pin_high(pin_sda);
42          io::delay_us(10);
43        }
44      }
45    }
46    const bool released = bus_released && io::pin_read(pin_sda) && io::pin_read(pin_scl);
```

- ループ条件が `!pin_read(pin_sda)` なので、SDA が High になった時点でクロック送出をやめる。
- I2C の read 中、スレーブは 1 のビットで SDA を離す。その直後に 0 のビットを送る場合、
  ループを抜けた後の STOP（`:35-42`）で SDA を離しても、スレーブが次の 0 ビットで SDA を
  引き戻すため STOP が成立しない。`:46` で `false` になる。
- つまり「SDA が High = スレーブが解放した」という判定が誤り、というのが作者の指摘であり、
  コードと一致する。

呼び出し側：

- `probe_i2c_bus_present()`（`probe_hardware.inl:65` 付近）は、`sample()` が
  `scl_high && !sda_high` のときだけ `recover()` を呼ぶ（`probe_types.hpp:224-228`）。
  `recover()` は `release_held_sda()` を呼び、戻り値を使わずに再サンプルする
  （`probe_hardware.inl:88-96`）。したがって `false` はそのまま「バスなし」判定になる。
- `probe_i2c_ack()` も初回に `release_held_sda()` の戻り値を `cache.pullup_ok` に入れる
  （`:130-134`）。
- `recover_held_sda_and_resample()`（`:50-62`）は S3 の複数検出から呼ばれる。
  影響範囲は ToughC5 だけではない（作者の注意書きと同じ）。

## 3. 検証方法（host-level test）

実機・仮想デバイスが使えないため、`test/board_detect/support/detect_io.hpp` の I/O 差し替え
（`M5GFX_BOARD_DETECT_IO_HEADER`）を使い、`release_held_sda()` の実テキストをそのまま呼ぶ
ホストテストを書いた（`code/sim_slave.cpp`）。

モデル：

- 開始状態は SCL High / SDA Low（報告の `probe_i2c_bus_present()` 入口と同じ）。
- スレーブは SCL 立ち下がりで次のビットを提示する（0 なら SDA を Low に保持）。
- 8 ビット終了後は ACK スロットで SDA を離す。`write` 受信のケースだけは 9 クロック目に
  ACK を返し、その次で離す。
- 途中の STOP は無視する（作者の「0 のビットを送っている間は STOP が成立しない」想定と
  同じ最悪ケース）。
- 実装は `host_hardware::events` の GPIO 書き込みイベントを読み、実際の SCL エッジで
  ビットを進める。`pin_low` / `pin_high` はオープンドレインとして扱う。

実行：

```sh
c++ -std=c++11 -O2 -Wall -Wextra -Wno-unused-function -Wno-unused-parameter -pedantic \
  '-DM5GFX_BOARD_DETECT_IO_HEADER="support/detect_io.hpp"' \
  -include <repo>/test/board_detect/support/native_devices_io.hpp \
  -I<repo>/test/board_detect -I<repo>/test/board_detect/stubs -I<repo>/src \
  sim_slave.cpp -o sim_slave
```

3 つのツリーで同じテストを実行した：旧 `b48dce0`、作者提案（9 回）、上限だけ 10 回に変えた版。

## 4. 結果

| ケース | 旧 `b48dce0` | 提案（9 回） | 提案（10 回） |
| --- | --- | --- | --- |
| read 中 `0,0,1,0,...` | **false** / 3 パルス | true / 2 | true / 2 |
| read 中 `0,0,0,0,0,0,0,0` | true / 9 | true / 8 | true / 8 |
| `0,1,1,...` | true / 2 | true / 1 | true / 1 |
| write 中、9 クロック目に ACK | true / 10 | **false** / 9 | true / 10 |
| SDA を離さない | false / 10 | false / 9 | false / 10 |

- 旧コードの `false` は、ループ 2 クロック + STOP 1 パルス = 3 パルス目で発生する。
  作者の「1〜2 クロック目で SDA が High になり、STOP の後に SDA が Low に戻る」と一致。
- 提案パッチは報告ケースを 2 パルスで解放する。無限ループもしない（最悪 9 / 10 パルス）。
- 既存ホストテストは旧・提案 9・提案 10 のすべてで `33 passed`。つまり既存スイートは
  この多ビットケースを覆っていない（作者の「前後とも 33 本合格」と同じ）。

### 4.1 9 → 10 の境界

旧コードは「9 クロックのループ + 独立した STOP」で最大 10 パルス。提案パッチは各クロックが
STOP を兼ねるため最大 9 パルスで、1 パルス減る。read 中は「残りデータビット + マスターが
駆動する ACK」で最大 9 パルスに収まるが、**スレーブが write を受信中**の場合は 9 クロック目に
スレーブ自身が ACK で SDA を Low に保持する。同じ「途中の STOP を無視する」仮定では、9 回で
打ち切ると解放に失敗する。上限を 10 にすると、このケースもモデル上は通る。

これは実機で確認した不具合ではなく、モデル上の境界。ただし追加コストは 1 クロックだけで、
旧コードの余裕を保てるため、公開コメントで提案した。

## 5. 影響範囲

- `release_held_sda()` は ToughC5 専用ではない。`probe_i2c_bus_present()`（ESP32 TimerCam、
  S3 PowerHub、C6 画面付きボード、C61 CoreMatrix、P4 CoreP4X / StampP4XHub / Tab5）と
  `recover_held_sda_and_resample()`（S3 の複数判定）から使われる。
- 変更されるのは「SDA が張り付いていたとき」の解放手順のみ。SDA が High のときの動作は同じ。
- 途中の STOP を無視するスレーブに対しては、旧コードより多くのクロックで解放を試みる。
  正常なバス（SDA が High）では追加のクロックは出ない。

## 6. 環境と再現性

- macOS、clang（`c++`）、C++11。M5GFX `b48dce0` を GitHub から取得。
- 実機なし。Device Service の 36 profile に C5 なし。esp-emulator の `devices/` に
  `esp32-c5` なし。LP I2C と ST25R3916 のモデルなし。
- 作者の実機表（ToughC5 + UnitNFC、30 回リセット）は引用のみ。こちらでは再現していない。
- 作者提案パッチは `b48dce0` に `git apply --check` で合格。

## 7. 未覆盖项とリスク

- hardware validation：`NOT RUN`。C5 実機・UnitNFC がない。
- virtual-device validation：`NOT RUN`。C5 profile と LP I2C / ST25R3916 モデルがない。
- 他ボードの実機影響：`NOT RUN`。特に P4 の `recover_held_sda_and_resample` 経路。
- write 中 ACK の境界：ホストモデルのみ。実機の ACK タイミングでは未確認。
- PR #423 との同時投入：`NOT RUN`。
- モデルはビット遷移を単純化しており、立ち上がり時間・クロックストレッチ・ST25R3916 の
  内部状態は再現しない。したがって「モデルで通った = 実機で直る」ではない。

## 8. タイムライン

- 2026-11-16 16:44 UTC：GOB52 が #424 を起票（OPEN、コメント 0）。
- 2026-11-17 00:5x CST：`b48dce0` を取得、コード確認、ホストモデル作成、3 変種で実行、
  既存 33 本を 3 変種で実行。
- 2026-11-17：公開コメントを 1 条投稿（Issue は OPEN のまま、コード変更・push なし）。
