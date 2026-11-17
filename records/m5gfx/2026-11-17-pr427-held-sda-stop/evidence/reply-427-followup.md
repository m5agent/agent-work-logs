追加ケースを確認しました。`fa2bc69` の差分は `test/board_detect/held_sda_release.cpp` と
`test/board_detect/README.md` だけで、`release_held_sda()` 本体は `b8f5d89` のままです。

**証拠レベル：host-level test**（hardware validation / virtual-device validation は引き続き NOT RUN）

- `sh test/board_detect/run.sh` → `C++ test programs: 34 passed`、`held_sda_release` 単体 → `44 cases passed`（ご報告の数字と一致）
- 追加ケースは `held_sda_release.cpp:110-112` で、9 ビットすべて Low を駆動し続けるスレーブに対して `false` と「ちょうど 10 パルス」を要求しています。起動時に無限ループしないことがテストで固定されました。
- このケースが上限を実際に拘束することも確認しました。ループ条件を `++i < 11` に変えると `pulses == 10` で `assert` 失敗（`held_sda_release.cpp:112`、exit 134）。上限を 1 増やす退行を検出できます。
- head `fa2bc69` の CI は 27 チェックすべて success（fail / pending なし）。

ブロッカーはありません。実機・仮想デバイスでの再現と、本文で未確認とされているボードは引き続き未確認です。

（投稿済み: <https://github.com/m5stack/M5GFX/pull/427#issuecomment-6942784653>）
