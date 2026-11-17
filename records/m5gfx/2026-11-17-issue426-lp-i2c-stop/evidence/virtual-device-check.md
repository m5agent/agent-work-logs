# 仮想デバイスで検証しなかった理由

- 本機の Device Service は 36 個の device profile を返し、SoC は ESP32 / ESP32-S3 /
  ESP32-C6 / ESP32-P4 / RP3A0 のみで、ESP32-C5 の profile はない。
  （C5 用のボード定義・フラッシュ手順・シリアル経路がない）
- esp-emulator の `devices/` は `esp32-c6` / `esp32-lx6` / `esp32-p4` / `esp32-s3` などを
  持つが ESP32-C5 の QEMU 機はない。`devices/` と `third_party/upstream` を
  `lp_i2c` / `LP_I2C` で検索してもモデル実装は 0 件で、C6 / P4 の LP I2C コントローラも
  モデル化されていない。
- この不具合は「LP IO ドメインが焊盘を所有している間、デジタル GPIO の操作が焊盘に
  届かない」という路由層の挙動に依存する。GPIO レベルの仮想モデルでは、たとえ C5 の
  機械を追加しても、LP IO MUX と LP I2C の接続を再現しない限り意味のある判定にならない。
- したがって hardware validation と virtual-device validation はどちらも `NOT RUN` とし、
  固定 commit のソースと ESP-IDF v5.5 の実装照合（code-level verification）だけで報告した。
