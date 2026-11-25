# 复现文件

脚本要求 macOS 的 `cp -cR`、Python 3.12、Node 和 Playwright。在独立模拟器工作树中准备下列受校验的输入。

- 按 [0043 构建记录](../../2026-11-25-cores3-qvga-camera/evidence/locked-build.summary.json) 重建，缓存置为 `.work/docs-wasm-cores3-camera-lab/locked-0043-build`，Emscripten 3.1.50 置为 `.work/docs-wasm-arduino-20261125/emsdk`。
- 在 `42dd0b8c…` 预览工作树用该运行时及 LittleFS 导出标准工作台，输出为 `.work/docs-wasm-adv-gnss-lab/sealed-site`，基路径 `/gnss-check/`。锁定站点身份见[原 GPS 记录](../../2026-11-25-cardputer-adv-gnss/)。本地复现要求基站清单 SHA-256 `decd60ad…594f`。
- 在 `.work/docs-uiflow-20261125/upstream` 检出 [固定 UIFlow2 修订](https://github.com/m5stack/uiflow-micropython/tree/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6)。ROM 与基础固件按导出清单的公开 URL 下载后分别放在 `.work/docs-wasm-arduino-20261125/esp32s3_rev0_rom.bin` 与 `.work/docs-wasm-cardputer-cc1101-lab/cardputer-adv-v2.5.3-base.bin`。两者由脚本在浏览器启动前核对完整 SHA-256。
- 将本目录中的脚本和补丁放进模拟器的 `.work/docs-wasm-cardputer-lora-lab`。复制 0043 的 `hw/m5stopwatch/m5cardputeradv.c`、`m5_sx1262.c` 和 `m5stopwatch.h` 到其 `preimage/hw/m5stopwatch` 及 `source/hw/m5stopwatch`，将补丁只应用到 `source`。两个目录的文件内容由构建脚本对照锁定预览检查。

```sh
cd .work/docs-wasm-cardputer-lora-lab
git -C source init -q
git -C source apply --check ../0098-cardputer-adv-sx1262-preview.patch
git -C source apply ../0098-cardputer-adv-sx1262-preview.patch
python3 check-sx1262-host.py
python3 build-lora-preview.py --name lora-preview-build-replay
python3 stage-lora-preview.py lora-preview-build-replay lora-preview-site-replay
node run-dual-lora.mjs lora-preview-site-replay pair-output-1262-replay lora1262
node run-dual-lora.mjs lora-preview-site-replay pair-output-868-replay lora868
```

重跑须选择新缓存和输出目录。浏览器脚本通过工作台真实启动、导入原 Python、工作台按键、固定 SX1262 对端操作及真实数据面运行。在重新构建产生新运行物时，使用其专属凭据重新执行例程。
