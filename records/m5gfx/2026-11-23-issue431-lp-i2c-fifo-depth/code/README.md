# 主机验证代码

把 M5GFX 两个 commit 的 `isLpPort()` / `getFifoLen()` **原文**抽出，按 ESP-IDF
各芯片真实宏值编译执行，观察返回值。

- base：`452c15bc982af0b54acf567a79e7eb6066ace9e5`（issue 报告时的 develop）
- head：`43a87193f898f998edf79c5fb99b166d11ee1eaf`（当前 develop，含 #432 / #433）

## 文件

| 文件 | 说明 |
| --- | --- |
| `extract.py` | 从指定 checkout 抽取两个函数，生成 `funcs_base.inc` / `funcs_head.inc` |
| `funcs_base.inc` / `funcs_head.inc` | 已抽好的原文（与上列 commit 对应） |
| `main_base.cpp` / `main_head.cpp` | 打印 port 0..3 的 `getFifoLen()`，并重算分块 |
| `run.sh` | 7 组宏配置的编译与执行 |
| `unknown.cpp` / `unknown_base.cpp` | 「LP 端口但无深度宏」的合成配置 |

## 重跑

`extract.py` 里的 `REPO` 指向本机 M5GFX checkout，按需修改后再执行；
`funcs_*.inc` 已随记录提交，可跳过抽取直接：

```bash
bash run.sh
```

宏值来自 ESP-IDF v6.1 的 `soc_caps.h` / `hal/i2c_ll.h` 与 v5.5.4 的 `soc_caps.h`，
详见 `../evidence/idf61-headers.txt`、`../evidence/idf554-c5-headers.txt`。

预期：

- base：所有 6.x 配置均为 `32 32 32 32`（C2 也是 32，即报告的静默降级）
- head：C5/C6 LP=16、P4 LP(port2)=16、C2=16、ESP32=32、5.5.4 配置不变
