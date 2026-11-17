# M5GFX #427: `release_held_sda()` が STOP 成立までクロックを出し続ける変更（ホスト検証）

- 日期：`2026-11-17`
- 结果：`PARTIAL`（host-level test で変更内容と回帰なしを確認。hardware / virtual-device は `NOT RUN`）
- 工作类型：`pr`
- 条目：[m5stack/M5GFX#427](https://github.com/m5stack/M5GFX/pull/427)
  「board_detect: SDA の解放で、STOP が成立するまでクロックを出し続ける」，作者 GOB52，日文，
  OPEN，レビュー・コメント 0 件（取得時）
- 源码：PR head `b8f5d89d516e8d88babec9c08103a9a6e52b5e9f`，
  base `develop` `21213080fba00c675d5dcca0ef2abd4b349e3cef`（#423 のマージ後、当時の develop 先端と一致）
- 环境：macOS、clang C++11。ESP32-C5 実機なし、Device Service に C5 profile なし

## 结论

1. 変更は #424 で合意した方針（各クロックの末尾で STOP を試し、SDA が High のまま残るまで
   繰り返す。上限は 9 ビット + ACK 用の 1 クロック）と一致する。
   `src/board_detect/probe_hardware.inl:31-41` の `do { ... } while (!io::pin_read(pin_sda) && ++i < 10);`
   がそれで、最大 10 パルスで終了する。
2. 同梱テスト `test/board_detect/held_sda_release.cpp` は本物の `release_held_sda()` に対して
   43 ケース合格。`sh test/board_detect/run.sh` は 34 本すべて合格（PR head）。
3. このテストは旧コードを実際に検出する。`develop` `b48dce0` の `release_held_sda()` に差し替えると
   最初のケース（`0x2D` の先頭 0 ビットから）で `assert` 失敗（`held_sda_release.cpp:90`、exit 134）。
4. 独立に用意した別モデル（#424 用に自作、スレーブが 1 バイト送信中のリセット状態をイベント列で再生）
   でも PR コードは 5/5 合格。issue ケース 2 クロック、全 0 バイト 8、write ACK 10、
   SDA 永久保持 10 クロックで `false`、SCL 保持は 0 クロック。
5. 呼び出し側 3 箇所はいずれも判定開始前（`probe_i2c_bus_present` の recover、
   `recover_held_sda_and_resample`、`probe_i2c_ack` の初回 pull-up 検査）で、余分なクロックが
   既存トランザクションを壊す経路はない。SCL が外部に Low 保持されている場合はクロックを出さず
   `false` を返す（従来どおり）。
6. ブロッカーなし。任意の改善として「10 クロック後も SDA を放さない周辺」ケースが同梱テストに
   無い点を挙げた（ループ終了上限だけがテストされていない。こちらでは別モデルで 10 パルス後に
   `false` を返すことを確認済み）。

## 关键证据

- `evidence/function-diff.patch`：`release_held_sda()` の差分（+12/-15）と、コメントの更新。
- `evidence/source-lines.txt`：PR head の関数全文と、比較用の `develop` `b48dce0` 版。
- `evidence/host-run-pr427.log`：PR head での `sh test/board_detect/run.sh` 全出力
  （`C++ test programs: 34 passed`）。
- `evidence/held-sda-pr427.txt`：`held_sda_release.cpp` 単体（`43 cases passed`）。
- `evidence/held-sda-develop.txt`：同じテストを `b48dce0` の関数で実行した結果
  （`Assertion failed ... held_sda_release.cpp, line 90`、exit 134）。
- `evidence/sim-independent-pr427.txt`：独立モデル `code/sim_slave.cpp` の生出力（failures=0）。
- `evidence/build-commands.txt`：再実行できるビルド／実行コマンド。
- `evidence/pr-427-meta.json`：PR メタデータ（本文・コメントは保存しない）。`evidence/commits.txt`：対象コミット。
- `evidence/platform-coverage.txt`：Device Service 36 プロファイルの SoC 一覧（C5 なし、C6 は
  `nanoc6` / `nesso-n1`）と esp-emu の QEMU バックエンド一覧（`esp32s3` / `esp32c6` / `esp32` /
  native / raspi3b、`esp32-c5` なし）。
- 已发布回复：下記「結果」参照

## 文件

- `report.md`：機序、コード位置、検証方法、影響範囲、未覆盖项
- `run.json`：構造化状態
- `code/sim_slave.cpp` / `code/README.md`：再実行できる独立ホストモデル
- `evidence/`：差分、ソース抜粋、実行ログ、環境の網羅状況

## 未覆盖项

- hardware validation：`NOT RUN`。ToughC5 + UnitNFC、Nesso N1 の内蔵 IMU リセット試験は
  再現していない。PR 本文の表（ToughC5 `0/70`、Nesso N1 `0/40` など）は作者の実機測定で、
  こちらでは測っていない。
- virtual-device validation：`NOT RUN`。ToughC5 (ESP32-C5) は実機も Device Service の
  36 プロファイルにも無く、esp-emu の QEMU バックエンドにも `esp32-c5` がない。C6 の
  プロファイルはあるが、「リセットが内部 IMU の read 中に当たり周辺が SDA を保持した」ピン状態を
  注入する手段がないため、この修正の効果は仮想デバイスでは確認できない。
- PR 本文で未確認とされているボード（TimerCam / PowerHub / Cardputer 無印 / VAMeter /
  StampS3Bat / PaperS3 / PaperDIY / UnitC6L / CoreMatrix / CoreP4X / StampP4XHub）：
  `NOT RUN`。
- write 受信中にリセットが当たる場合：host モデルのみ。実機の ACK タイミングは未確認。
- 実機の立ち上がり時間・クロックストレッチ・UnitNFC (ST25R3916) 固有挙動：モデル化していない。
