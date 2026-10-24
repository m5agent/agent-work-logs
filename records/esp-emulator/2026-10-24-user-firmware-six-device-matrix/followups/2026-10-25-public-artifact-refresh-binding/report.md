# ESP Emulator public firmware refresh and SHA binding report

## 背景

同一个 M5Burner `firmware_id` / `version_id` 对应的 CDN BIN 可以变化。
原先普通运行会强制刷新，但 `--resume` 直接读取旧 `plan.json` 和缓存
`device:firmware` 键，仍可能复用旧字节。

## 实现

- 抽取出 `refresh_selected_sample()`；
- resume 保留原样本选择，但依次强制下载并重新分析当前 BIN；
- refreshed plan 原地持久化新路径、SHA、metadata 和 static analysis；
- result key 改为 `device:firmware:sha256`；
- SHA 变化后旧 sample result 不匹配，必须重新执行；
- 下载、分析或 target slug 变化时 resume fail-closed。

## 当前四个公开 BIN

| Device | Firmware ID | Source SHA256 | Manifest artifact SHA256 | Result |
| --- | --- | --- | --- | --- |
| AtomS3R | `1897200000000002559` | `74e714...dae4` | `17ddf5...8e7` | Manifest PASS / functional NOT RUN |
| AtomS3R | `1897200000000000358` | `b3597f...59b3` | `9b2d73...e286` | Manifest PASS / functional NOT RUN |
| PaperMono | `1897200000000000015` | `06eb3b...6986` | same | Manifest PASS / functional NOT RUN |
| PaperMono | `2091144466157694978` | `e2dee3...e935` | `0fc4c9...b118` | Manifest PASS / functional NOT RUN |

两个 sparse 样本归一化为 8/16 MiB 全 Flash 后 artifact SHA 与下载源 SHA
不同，因此两份 hash 都必须保留。

## 验证

```text
user firmware matrix 15/15 PASS
documentation consistency 19/19 PASS
platform suite 351/351 PASS
GitHub Actions 40113705698 PASS
```

四个 manifest validation PASS，但 static review 均为
`REVIEW_REQUIRED`；两个 samples 的 filesystem inventory 为
`INVALID` / `UNFORMATTED`，一个 sample 的 filesystem inventory PASS，
one sample has no data filesystem.

## 边界

- static analysis / manifest PASS 不等于 boot、frame、input 或 application PASS。
- 当前 4 个 BIN 未通过 Device Service 执行。
- 公开样本数量和历史 PASS/PARTIAL 不自动继承到当前 SHA。

## 回滚

回退源码提交
`b8dbc2d0d6fad12f341145a6c25e2d91e48c45ba`。
