# 報告：M5GFX #427 `release_held_sda()` の STOP 成立までクロック継続

## 1. 対象と背景

`m5stack/M5GFX#427` は、issue #424 で報告された「ボード判定時に、リセットで転送の途中に
取り残されたスレーブが SDA を Low に保持していると、解放処理が STOP を成立させられない」
問題に対する修正 PR。作者は #424 の報告者と同じ GOB52。

変更は 3 ファイル。

| ファイル | 変更 |
| --- | --- |
| `src/board_detect/probe_hardware.inl` | `release_held_sda()` のループを「SDA が High になるまでクロック」から「各クロック末尾で STOP を試し、成立するまで繰り返す」に変更（+12/-15） |
| `test/board_detect/README.md` | 新テストの行を追加 |
| `test/board_detect/held_sda_release.cpp` | 新規ホストテスト（118 行） |

base は `develop` `2121308`（#423 のマージ済み）。レビュー時点の `refs/heads/develop` も
`2121308` で、差分の適用先にずれはない。

## 2. 機序

旧コードは SDA が一度 High になった時点でクロックを止め、独立に 1 回 STOP を出していた。
read の途中で取り残されたスレーブは送信中のバイトの続きを出しており、SDA が High になるのは
そのバイトの 1 のビットでもある。STOP のために SCL を下げるとスレーブは次の 0 ビットで SDA を
再び Low にするため、STOP が成立しない。`release_held_sda()` は `false` を返し、
バスがないと判断されたボードは判定から外れる（ToughC5 / Nesso N1 で `getBoard() == 0x00`）。

新コードは 1 クロックごとに「SCL Low → SDA Low → SCL High → SDA High（STOP）」を行い、
SDA が High のまま残るまで繰り返す。スレーブは遅くとも ACK の位置で SDA を離すので
9 クロック以内に解放され、write 受信中で自分の ACK を保持しているスレーブのために
1 クロック余裕を足して上限 10。

## 3. コード確認（PR head `b8f5d89`）

```c
bool bus_released = io::pin_read(pin_scl);
if (bus_released && !io::pin_read(pin_sda))
{
  int i = 0;
  do
  {
    io::pin_low(pin_scl);
    io::delay_us(5);
    io::pin_low(pin_sda);
    io::delay_us(5);
    if (!wait_i2c_scl_high(pin_scl)) { bus_released = false; break; }
    io::pin_high(pin_sda);
    io::delay_us(10);
  } while (!io::pin_read(pin_sda) && ++i < 10);
}
const bool released = bus_released && io::pin_read(pin_sda) && io::pin_read(pin_scl);
```

- STOP は「SCL High の間に SDA を Low → High」で形成される。SDA を駆動 Low にするのは
  SCL Low の区間だけで、SCL High の区間では必ず手放す。START/STOP の取り違えはない。
- `++i < 10` で最大 10 パルス。#424 で指摘した write 受信中の ACK（10 パルス目）をちょうど覆う。
- `wait_i2c_scl_high()` が失敗した場合は `bus_released = false` で即抜け、無限ループしない
  （このとき SDA は Low 駆動のまま抜けるが、呼び出し側 3 箇所はいずれも
  `restore_to_snapshot()` でピン状態を戻す）。
- 入口で SCL が Low（外部保持）の場合はクロックを出さず `false`。従来と同じで、テストでも
  `pulses == 0` を確認している。
- 呼び出し側：`probe_i2c_bus_present` の `recover`、`recover_held_sda_and_resample`、
  `probe_i2c_ack` の初回 pull-up 検査。いずれも判定開始前で、バス上に自分が開始した
  トランザクションはない。最大 10 パルス（各 ~25 µs、最悪でも SCL 待ち 25 ms が 1 回）は
  起動時間に影響する水準ではない。

## 4. 実行結果（host-level test）

環境：macOS、clang C++11。`test/board_detect/run.sh` は各 `.cpp` を単体ビルドして実行する。

| 実行 | 結果 |
| --- | --- |
| `sh test/board_detect/run.sh`（PR head `b8f5d89`） | `C++ test programs: 34 passed`（exit 0） |
| `held_sda_release.cpp` 単体（PR head） | `held SDA release: 43 cases passed` |
| `held_sda_release.cpp` 単体（`b48dce0` の旧関数に差し替え） | `Assertion failed ... held_sda_release.cpp, line 90`、exit 134 |
| 独立モデル `code/sim_slave.cpp`（PR head、#424 で自作） | 5/5 合格、`failures=0` |

旧関数での失敗は最初のケース（`0x2D` = `0010 1101` の先頭 0 ビットから開始）で起きる。
旧コードは 2 クロック目で SDA が High になった時点で止まり、続く 0 ビットで SDA を再度
Low にされるため STOP が成立しない。新テストが不具合を実際に検出していることの証拠。

独立モデルの内訳（SCL 立ち下がり数、STOP を含む）：

| ケース | released | clocks |
| --- | --- | --- |
| `0,0,1,0,...`（報告ケース） | true | 2 |
| `0,0,0,0,0,0,0,0` | true | 8 |
| `0,1,1,...`（1 クロックで解放） | true | 1 |
| write 中、9 クロック目に ACK | true | 10 |
| SDA を離さない（永久保持） | false | 10 |

同梱テストとの違い：作者のテストは `host_hardware::events` を再生するピンレベルのモデルで、
UnitNFC の `0x2D` / `0x93` の各 0 ビット位置、write 受信 ACK、SCL 保持、アイドルを網羅する。
一方「永久に SDA を離さない周辺」ケースが無く、ループの終了上限（10 パルス）だけは
テストで固定されていない。独立モデルで 10 パルス後に `false` を返すことを確認したので、
任意の改善として 1 ケース追加を提案した。

## 5. 互換性・影響範囲

- 変更は `release_held_sda()` の中だけ。SDA が保持されていない場合の動作は不変
  （入口の `if` で即 `released`）。
- `release_held_sda()` を使う判定は全ボード共通の経路で、ボード固有分岐はない。
  差分は 3 ファイルのみで、スナップショットや生成物の更新は含まれない。
- CI（PR #427 の checks）は、カタログ生成、IDF 5.1.6 / 5.4.3 / 6.0.2、Arduino-ESP32
  2.0.17 / 3.1.3、C3 / C5 / C6 / C61 / H2 / P4 / S3 のビルドがすべて pass。

## 6. 未覆盖项とリスク

- hardware validation：`NOT RUN`。ToughC5 (ESP32-C5) + UnitNFC、Nesso N1 の内蔵 IMU を
  使った「read 中リセット」試験は再現していない。PR 本文の表は作者の実機測定で、こちらは
  引用のみ。
- virtual-device validation：`NOT RUN`。Device Service の 36 プロファイルに C5 が無く、
  esp-emu の QEMU バックエンドも `esp32s3` / `esp32c6` / `esp32` / native / raspi3b のみ。
  C6（`nesso-n1` / `nanoc6`）のプロファイルはあるが、「リセットが転送中に当たり周辺が
  SDA を保持した」ピン状態を注入する手段がなく、この修正の効果は確認できない。
- write 受信中にリセットが当たるケース：host モデルのみ。
- 立ち上がり時間、クロックストレッチ、ST25R3916 固有の挙動：モデル化していない。
- PR 本文で未確認とされている 11 ボード：`NOT RUN`。

## 7. 判定

ブロッカーなし。host テストで旧コードの失敗と新コードの解放・上限・終了が確認でき、
既存 33 テストおよび CI のビルドにも回帰はない。実機での再現は未実施である点を明示して
日文で 1 条のコメントを投稿した（PR は OPEN のまま、close / push はしない）。

## 8. 追加ラウンド（`fa2bc69`、2026-11-17）

第 1 ラウンドで「任意」として挙げた「10 クロック後も SDA を放さない周辺」ケースを作者が
追加した。差分は `test/board_detect/held_sda_release.cpp`（+3）と
`test/board_detect/README.md`（+1/-1）のみで、`src/board_detect/probe_hardware.inl` は
`b8f5d89` のまま。修正本体の挙動は変わっていない。

追加ケースは、9 ビットすべてで SDA を Low に駆動し続けるスレーブ（受信側、start 0、SCL は
正常）に対して、`release_held_sda()` が `false` を返し、SCL パルスがちょうど 10 回であることを
要求する（`held_sda_release.cpp:110-112`）。

確認結果（head `fa2bc69`）:

- `sh test/board_detect/run.sh` → `C++ test programs: 34 passed`
- `held_sda_release` 単体 → `held SDA release: 44 cases passed`（作者の報告と一致）
- 変異テスト：ループ条件を `++i < 10` から `++i < 11` に変えると、追加ケースが
  `pulses == 10` で `assert` 失敗（`held_sda_release.cpp:112`、exit 134）。上限を 1 増やす
  退行をこのケースが検出できる。
- CI（head `fa2bc69`）：27 チェックすべて success、fail / pending なし。

未覆盖は第 6 節と同じ。hardware / virtual-device は引き続き `NOT RUN`。

## 9. 第 3 ラウンド（ainyan03 の ESP32-P4 実機報告、2026-11-17）

PR のコメント
<https://github.com/m5stack/M5GFX/pull/427#issuecomment-6943480159>
で、ainyan03 が ESP32-P4 実機での再現と修正確認を報告した。これは m5agent の測定ではなく、
著者側の `hardware validation` である。

### 9.1 報告の内容

- 環境：ESP32-P4 (rev 3.2)、Arduino (pioarduino `55.03.312`)、M5GFX develop `2121308` に
  #424 の差し替え後の修正案（`probe_hardware.inl` の差分はこの PR と同じ）を当てたもの。
- 内部 I2C は GPIO11 = SDA / GPIO9 = SCL（HP ポート）。ボード判定は PM1 (0x6E)、
  取り残されるスレーブは同じバスの BMI270 (0x68)。SDA / SCL をロジックアナライザで記録。
- 状態の作り方：BMI270 の `0x46` (FIFO_WTM_0) に保持させたい値を書き、`0x45` を指して
  read を開始して 1 バイト受けて ACK を返し、SCL を離して STOP を出さずに `esp_restart()`。
  スレーブは `0x46` の値の先頭ビットを出したまま待つ。
- 結果：`0x55` は develop で 4/4 誤判定（表示器なし）→ この PR で 4/4 正判定。`0x2A` は
  1/1 誤判定 → 1/1 正判定。`0x02` は develop でも正判定（1 回目は失敗、2 回目に ACK の
  位置でスレーブが SDA を離した）。
- develop の `0x55` は解放の試みが 2 回あり、どちらも 2 クロックで打ち切られ、1 のビットで
  SDA が High になった時点で STOP に移り、その間に次の 0 ビットで Low に戻されていた。
  この PR では最初の試みが 1 クロックで STOP まで成立した。
- 未確認：write の受信中に取り残されたスレーブ、ESP32-S3 の
  `recover_held_sda_and_resample()` の経路。

### 9.2 コード側の照合

`fa2bc69` の `src/board_detect/probe_hardware.inl` は `b8f5d89` と同一の blob
`cb8577113cf72abfaaa7cdaae9ac02b8a46ad9a6`。base `2121308` の blob は
`437cb85547b0f5bf396bc7439b275e840184b066` で、PR の差分（+12/-15）はこのファイルを含む。
したがって、報告が当てた差分と PR の修正本体は同じファイル内容である。また `2121308` と
`b48dce0` の `probe_hardware.inl` は diff がなく、報告の develop とこちらで使った旧コードは
同じ関数内容である。

報告の状態を `code/owner_report_check.cpp` でモデル化した。マスターが 1 バイトを ACK した後、
スレーブが次のバイトの MSB を出して待っている状態から、`release_held_sda()` を 2 回続けて
呼ぶ（報告の 2 回の解放試行に合わせる）。SCL の立ち下がりで次のビットに進み、8 データビットの
後の ACK スロットで SDA を離し、NACK または STOP で送信を止める。

| 保持値 | develop `b48dce0` | `fa2bc69` |
| --- | --- | --- |
| `0x55` | 1 回目 2 パルスで `false`、2 回目も 2 パルスで `false` | 1 パルスで `true` |
| `0x2A` | 1 回目 3、2 回目 2 パルスで `false` | 2 パルスで `true` |
| `0x02` | 1 回目 7 パルスで `false`、2 回目 2 パルスで `true`（ACK 位置） | 6 パルスで `true` |

生出力は `evidence/owner-report-check-old.txt` / `-new.txt`。報告の「`0x55` は 2 クロックで
打ち切り」「`0x02` は 2 回目に ACK の位置で離す」と一致し、新コードは最初の 1 ビットで
止まらず、同じクロックのうちに STOP が成立する。これは実機の電気的挙動ではなく、
GPIO イベント列に対する host モデルの結果である。

### 9.3 未確認とされていた 2 点

- **write 受信中**：I2C の write でスレーブが SDA を駆動するのは ACK スロットだけなので、
  リセットで保持され得るのは ACK の間だけである。同梱テストの「ACK を保持する受信側」が
  その形で、解放は ACK のクロックで起きる。実機の ACK タイミングは未確認のままだが、
  上限 10 パルスは 9 ビット + ACK 1 クロックの余裕を含む。
- **ESP32-S3 の `recover_held_sda_and_resample()`**：この関数は `release_held_sda()` を
  呼ぶだけで（`probe_hardware.inl:55`）、戻り値を使わずピン状態を再サンプルする。呼び出しは
  `esp32s3.inl:428,675,757,761` の 4 箇所（PMIC 判定、Paper 系、Cardputer のサブ division）。
  修正はこの経路にもそのまま入り、別実装の変更は要らない。解放できなかった場合も再サンプル
  結果は従来と同じで、余分なクロックは最大 10 回に収まる。実際に SDA を保持させた S3 実機
  確認は未実施（報告の StickS3 / CardputerADV は 0/40 で、この経路の効果を直接は示さない）。

### 9.4 仮想デバイス

Device Service には `tab5` (ESP32-P4NRW32, esp-emulator-native) のプロファイルがあるが、
サービスは `tab5_enabled: false` を返し、この環境では起動できない。加えて、リセットが
転送中に当たって周辺が SDA を保持したピン状態を注入する手段がないため、この修正の効果は
仮想デバイスでも確認していない（`NOT RUN`）。

### 9.5 判定

ブロッカーなし、は変わらない。hardware validation は著者側の P4 1 ボード分が追加され、
m5agent 自身の実機・仮想検証は引き続き `NOT RUN`。残る未確認は write 中 ACK、S3 の保持
SDA 経路、PR 本文の 11 ボードで、いずれもマージのブロッカーではない。

日文で 1 条のコメントを投稿した（2026-11-17T09:07:54Z、
<https://github.com/m5stack/M5GFX/pull/427#issuecomment-6943645133>）。PR は OPEN のまま、
close / 上流への push はしていない。
