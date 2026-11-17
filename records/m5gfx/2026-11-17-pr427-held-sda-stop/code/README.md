# 独立ホストモデル（#424 で自作、#427 の確認に再利用）

`sim_slave.cpp` はスレーブ 1 台だけをモデル化する。スレーブはリセット時点のビット位置から
1 バイトを送信しており、SCL の立ち下がりで次のビットへ進み、ACK の位置で SDA を離す。
マスターが SCL High の間に SDA を Low → High にした場合だけ STOP とみなして停止する
（途中の STOP を無視してバイトを続ける、issue の最悪ケース）。

対象コードは `release_held_sda(int pin_sda, int pin_scl)` の実体で、
`test/board_detect/support/native_devices_io.hpp` の `host_hardware`（GPIO イベント記録）に
対して動かす。モデルは SDA / SCL のライン状態を `host_hardware::events` から再生する。

## ビルドと実行

M5GFX のソースツリー（PR head）で、リポジトリのルートから：

```sh
c++ -std=c++11 -O2 -Wall -Wextra -Wno-unused-function -Wno-unused-parameter -pedantic \
  '-DM5GFX_BOARD_DETECT_IO_HEADER="support/detect_io.hpp"' \
  -include test/board_detect/support/native_devices_io.hpp \
  -Itest/board_detect -Itest/board_detect/stubs -Isrc sim_slave.cpp -o sim_slave
./sim_slave
```

`failures=0` で終了コード 0。内訳（SCL 立ち下がり数、STOP を含む）：

| ケース | released | clocks |
| --- | --- | --- |
| `0,0,1,0,...`（報告ケース） | true | 2 |
| `0,0,0,0,0,0,0,0` | true | 8 |
| `0,1,1,...`（1 クロックで解放） | true | 1 |
| write 中、9 クロック目に ACK | true | 10 |
| SDA を離さない（永久保持） | false | 10 |

## 制約

- 立ち上がり時間、クロックストレッチ、スレーブ固有のタイミング（ST25R3916 など）は
  モデル化していない。実機の電気的挙動を示すものではない。
- このモデルは #424 の切り分け用に書いたもので、#427 の確認では
  author のテスト（`test/board_detect/held_sda_release.cpp`）とは独立な実装として使った。
