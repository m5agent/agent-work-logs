# M5GFX #424: `release_held_sda()` の STOP 成立条件とリセット取り残しスレーブ（ホスト検証）

- 日期：`2026-11-17`
- 结果：`PARTIAL`（host-level test で機序と修正案を再現・検証。hardware / virtual-device は `NOT RUN`）
- 工作类型：`issue`
- 条目：[m5stack/M5GFX#424](https://github.com/m5stack/M5GFX/issues/424)
  「ボード判定で、リセットで取り残されたスレーブの SDA を解放する処理が STOP を成立させない」，
  作者 GOB52，日文，OPEN，取得時コメント 0
- 源码：`develop` `b48dce04c80d3e3c9874b7ba946c43d672129c28`（0.3.0 の同区間は同一内容）
- 环境：macOS、clang C++11。ESP32-C5 実機なし、Device Service に C5 profile なし

## 结论

1. 報告された機序は `b48dce0` のコードと一致する。`release_held_sda()`
   （`src/board_detect/probe_hardware.inl:15`）は SDA が High になった時点でクロックを止める
   （`:27-32`）。これがデータの 1 ビットだと、続く 0 ビットで SDA が再び Low になり、
   後置の STOP（`:33-44`）が成立せず `false` を返す。
2. 自作のホスト・スレーブモデルで再現した。SCL High / SDA Low から始め、スレーブが
   `0,0,1,0,...` を送る場合、旧コードは 2 クロック目で打ち切り、STOP を含む 3 パルス目で
   `released=false`。作者の表の「1〜2 クロック目で SDA が High」と一致する。
3. 作者提案パッチ（各クロックで STOP を試し、最大 9 回）はこのケースを 2 パルスで解放する。
   M5GFX 既存ホストテスト 33 本は修正前後とも合格。
4. 境界を 1 点確認した。提案パッチは総パルス数が最大 9 で、旧コードの「9 クロック + 独立
   STOP = 最大 10 パルス」より 1 パルス少ない。スレーブが write 受信中で 9 クロック目に ACK を
   返す場合、同じ「途中の STOP を無視してバイトを続ける」仮定では 9 回で打ち切ると解放に
   失敗する（モデル上）。上限を 10 にすると read 中・write 中とも通る（モデル上、実機未確認）。
   → 公開コメントでは「9 → 10 の余裕を」と提案した。
5. PR #423 は `src/lgfx/v1/platforms/esp32/common.inl` のみを変更し、本ファイルとは独立。
   #423 を入れると read が正常化してリセットが転送中に当たりやすくなる、という作者の説明とも
   矛盾しない。

## ホストモデルの結果（SCL 立ち下がり数、STOP を含む）

| ケース | 旧 `b48dce0` | 提案（9 回） | 提案（10 回） |
| --- | --- | --- | --- |
| read 中 `0,0,1,0,...`（報告ケース） | **false** / 3 | true / 2 | true / 2 |
| read 中 `0,0,0,0,0,0,0,0` | true / 9 | true / 8 | true / 8 |
| `0,1,1,...`（1 クロックで解放） | true / 2 | true / 1 | true / 1 |
| write 中、9 クロック目に ACK | true / 10 | **false** / 9 | true / 10 |
| SDA を離さない | false / 10 | false / 9 | false / 10 |

モデルの前提：SDA は SCL 立ち下がりで次ビットに変わる、スレーブは ACK の後で SDA を離す、
途中の STOP は無視する（作者の想定と同じ最悪ケース）。立ち上がり時間、クロックストレッチ、
ST25R3916 固有の挙動はモデル化していない。

## 关键证据

- `evidence/source-lines.txt`：`release_held_sda`（`:15-48`）、`probe_i2c_bus_present` の
  recover 呼び出し（`:88-96`）、`probe_i2c_ack`（`:130-134`）、`recover_held_sda_and_resample`
  （`:50-62`）、呼び出し側 `probe_types.hpp:210-236`。
- `evidence/author-proposed.diff` + `evidence/author-patch-apply-check.txt`：
  `b48dce0` に対して `git apply --check` 合格。
- `evidence/host-run-baseline.txt` / `host-run-patched9.txt` / `host-run-patched10.txt`：
  `sh test/board_detect/run.sh` が 3 者とも `33 passed`。
- `evidence/sim-slave-baseline.txt` / `sim-slave-patched9.txt` / `sim-slave-patched10.txt`：
  上表の生出力。`code/sim_slave.cpp` がモデル本体。
- `evidence/issue-424.json`：条目メタデータ（本文はコピーしない）。
- `evidence/hardware-and-virtual.md`：C5 実機・profile がない理由。
- 已发布回复：<https://github.com/m5stack/M5GFX/issues/424#issuecomment-6923090635>（1 条，Issue 保持 OPEN、代码未改）

## 文件

- `report.md`：詳細な機序、コード位置、モデル、影響範囲、未覆盖项
- `run.json`：構造化状態
- `code/sim_slave.cpp` / `code/README.md`：再実行できるホストモデル
- `evidence/`：ソース抜粋、パッチ、実行ログ、境界メモ

## 未覆盖项

- hardware validation：`NOT RUN`。ToughC5 + UnitNFC の 30 回リセットは再現していない。
  作者の実機表（`0/30` → `2/30` など）は引用のみで、こちらでは測っていない。
- virtual-device validation：`NOT RUN`。Device Service に C5 profile がなく、esp-emulator にも
  `esp32-c5` がない。LP I2C と ST25R3916 のモデルもない。
- 他ボード（P4 / S3 の `recover_held_sda_and_resample` 経路）への実機影響：`NOT RUN`。
- 9 / 10 パルス境界：ホストモデルのみ。実機の ACK タイミングでは未確認。
- PR #423 と本修正の同時投入：`NOT RUN`（実機なし）。
- build：`NOT RUN`（C5 ツールチェーンなし）。
