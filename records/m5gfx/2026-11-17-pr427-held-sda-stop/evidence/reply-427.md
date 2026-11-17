変更内容を確認しました。`develop` `2121308` を base とする `b8f5d89` に対して、コードとホストテストの範囲ではブロッカーは見つかりませんでした。各クロックで STOP を試し、上限を 9 ビット + ACK 用の 1 クロックにする方針は #424 で合意した内容と一致しています。CI（C5 を含む 28 チェック）もすべて pass しています。

**証拠レベル：host-level test**（hardware validation / virtual-device validation は NOT RUN）

- `sh test/board_detect/run.sh` → `C++ test programs: 34 passed`
- `test/board_detect/held_sda_release.cpp` 単体 → `held SDA release: 43 cases passed`
- 同じテストを `develop` `b48dce0` の `release_held_sda()` に差し替えると、最初のケース（`0x2D` の先頭 0 ビットから開始）で `assert` 失敗（`held_sda_release.cpp:90`、exit 134）。追加テストが旧コードの不具合を実際に検出していることを確認しました。
- 別に用意したモデル（1 バイト送信中のリセット状態を GPIO イベント列で再生）でも 5/5 合格：報告ケースは 2 クロック、全 0 バイトは 8、write 受信中の ACK は 10、SDA を永久に放さない場合は 10 クロックで `false`、SCL 外部保持は 0 クロック。

**コード位置**：`src/board_detect/probe_hardware.inl:31-41`。SCL High の間に SDA を離して STOP を形成し、`++i < 10` で最大 10 パルス。`wait_i2c_scl_high()` の失敗時は `bus_released = false` で即抜けます。呼び出し側 3 箇所はいずれも判定開始前（開始済みトランザクションがない）なので、余分なクロックが既存の転送を壊す経路はありません。入口で SCL が外部に Low 保持されている場合はクロックを出さずに `false`（従来どおり、テストでも 0 パルスを確認）。

**提案（任意）**：`held_sda_release.cpp` には「10 クロック後も SDA を放さない周辺」のケースがなく、ループの終了上限だけがテストされていません。1 ケース追加しておくと、起動時に無限ループしないことがテストで固定できます（手元のモデルでは 10 パルス後に `false` を返すことを確認済みです）。

**未カバー**：実機・仮想デバイスは NOT RUN です。ToughC5 (ESP32-C5) は実機も Device Service の 36 プロファイルにも無く、esp-emu の QEMU バックエンドも `esp32` / `esp32c6` / `esp32s3` の 3 機種（ほかに native と raspi3b）のみです。C6（Nesso N1）のプロファイルはありますが、リセットが転送中に当たり周辺が SDA を保持したピン状態を注入する手段がないため、この修正の効果は仮想デバイスでは確認できません。本文の実機表と、未確認とされている 11 ボードはこちらでは再現していません。

詳細：https://github.com/m5agent/agent-work-logs/blob/26a18b6d312a8d9f48e61fd2ac5dace7f48141a3/records/m5gfx/2026-11-17-pr427-held-sda-stop/README.md
