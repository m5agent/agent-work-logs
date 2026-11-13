# 固定入口与复现命令

本记录使用现有源码 runner，无新增测试固件或产品补丁。复现应使用独立 checkout 与新输出目录，
不得覆盖本轮或历史报告。以下环境路径由复现者提供，不是本次机器路径。

固定源码：`70ef503fc2fb8b2c787fa9065e2952f525c40099`。Node `22.14.0`，Python `3.13.15`，
Playwright / Playwright Core `1.64.1`（按源码 package-lock 安装），
Google Chrome `157.0.8103.52`，exe SHA 见[资格摘要](../evidence/qualification-gates-summary.json)。
匹配此完整记录需使用相同浏览器字节；其他版本产生新的执行证据，不替代本轮结果。

准备相同导出必须使用[导出器](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tools/build_public_site.py)和
[运行资产清单](../evidence/runtime-assets-summary.json)中逐字节相同的三个 runtime 目录。
下载/构建方式按[固定构建说明](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/scripts/qemu-wasm-build/README.md)执行；若重建后的
资产不同，应单独定版完整验证，不能声称复现了相同产物。本记录没有分发 ROM 或原固件；
ROM 按 profile 中公开来源自行提供，原版 CoreMatrix BIN SHA 必须是
`0bfbe5a4acb467d93a7ded2186a4f73adea37511869328b563c15ab73163a018`。

```sh
# 在上述固定源码 checkout 根目录；这些变量由复现者设置为自有路径。
python3 platform/tools/build_public_site.py --output "$PAGES_SITE" \
  --base-path /m5stack-esp-emulator/ --service-url '' \
  --qemu-runtime "$PAGES_XTENSA_RUNTIME" --qemu-c61-runtime "$PAGES_C61_RUNTIME" \
  --littlefs-runtime "$PAGES_LITTLEFS_RUNTIME"
npm ci --prefix platform/tests
```

导出清单应为 `54fc8d8fe023ef0d86e3bfdea3d3db37599a2f59404c54fdb8920d466bd14a8c`；不匹配时停止并核对源文件和全部 runtime bytes。
下列 Python 命令以与实跑相同方式清理继承的 M5_* 诊断配置并顺序执行四个现有入口。
设置 `PAGES_SITE`、`PAGES_CHROME`、`PAGES_STOCK_BIN`、`PAGES_OUTPUT` 后，从固定 checkout 运行：

```sh
python3 - <<'PYCODE'
from pathlib import Path
import os, subprocess, hashlib
source = Path.cwd()
site = Path(os.environ['PAGES_SITE']).resolve()
chrome = Path(os.environ['PAGES_CHROME']).resolve()
stock = Path(os.environ['PAGES_STOCK_BIN']).resolve()
out = Path(os.environ['PAGES_OUTPUT']).resolve()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == '70ef503fc2fb8b2c787fa9065e2952f525c40099'
assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], text=True)
assert sha(site / 'public-site-manifest.json') == '54fc8d8fe023ef0d86e3bfdea3d3db37599a2f59404c54fdb8920d466bd14a8c'
assert sha(chrome) == '5441ca699b9eff7763f2f10765e2e8409a4b05f38917826b5247f6f6bb3b0c6b'
assert sha(stock) == '0bfbe5a4acb467d93a7ded2186a4f73adea37511869328b563c15ab73163a018'
out.mkdir(parents=True, exist_ok=False)
env = {k: v for k, v in os.environ.items() if not k.startswith('M5_')}
env.update(NODE_PATH=str(source / 'platform/tests/node_modules'),
           M5_PUBLIC_SITE=str(site), M5_PUBLIC_BASE_PATH='/m5stack-esp-emulator/',
           M5_WASM_GPU='hardware', M5_WASM_CHROME=str(chrome), M5_CHROME=str(chrome),
           PLAYWRIGHT_CHROMIUM_EXECUTABLE=str(chrome), M5_QEMU_READY_TIMEOUT_MS='600000',
           M5_QEMU_GATE_REQUIRE_ALL='1', M5_QEMU_GATE_WORKERS='1',
           M5_QEMU_GATE_PHASE='all', M5_QEMU_GATE_DEVICES='')
commands = [
 ('pixel', 'test_public_qemu_pixel_observer_browser.mjs', {'M5_CANVAS_TEST_OUT': str(out/'pixel')}),
 ('coi', 'test_public_coi_worker_browser.mjs', {'M5_COI_WORKER_BROWSER_OUT': str(out/'coi')}),
 ('corematrix-stock', 'test_public_qemu_corematrix_stock.mjs',
  {'M5_QEMU_UPLOAD': str(stock), 'M5_PUBLIC_QEMU_OUT': str(out/'corematrix-stock')}),
 ('all', 'test_public_qemu_admitted_boards.mjs', {'M5_PUBLIC_QEMU_OUT': str(out/'all')}),
]
for name, script, extra in commands:
    with (out/(name+'.log')).open('xb') as log:
        subprocess.run(['node', str(source/'platform/tests'/script)], cwd=source,
                       env={**env, **extra}, stdout=log, stderr=subprocess.STDOUT, check=True)
assert sha(chrome) == '5441ca699b9eff7763f2f10765e2e8409a4b05f38917826b5247f6f6bb3b0c6b'
PYCODE
```

上述是实际功能入口与参数的可重放形式；本次额外包装流程还在执行前后冻结源码、依赖和导出，
每 10 秒采样 Chrome 哈希并验证 75 份 child 报告闭集。复现完整 browser-provenance 资格也须
独立保存这些收据；仅成功执行上述命令不能自称已有相同的 393 次历史采样。

固定 runner：

- [完整 72 例调度器](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_qemu_admitted_boards.mjs)。
- [UIFlow 编辑器](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_uiflow_guest.mjs)和[按钮](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_qemu_buttons_guest.mjs)。
- [fixed 屏幕](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_qemu_board_guest.mjs)、[headless](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_qemu_headless_guest.mjs)、[CoreS3](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_qemu_guest.mjs)。
- [原版 CoreMatrix](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_qemu_corematrix_stock.mjs)。
- [pixel host 控制](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_qemu_pixel_observer_browser.mjs)、[COI host 控制](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_coi_worker_browser.mjs)。

终态应有全部 72 个 exit=0、报告 PASS、0 NOT RUN、无筛选、同一 site manifest，且每个
child report SHA 与实际字节相同。检查固件/profile/controller、真实输入/输出、serial/frame
与 iframe/Worker 清理，保留所有 FAIL。stock 的前 iframe pthread 缺项不能由其他用例补齐。
打包、公开发布、远端读回及 HTTPS guest 是独立步骤，本命令不执行它们。
