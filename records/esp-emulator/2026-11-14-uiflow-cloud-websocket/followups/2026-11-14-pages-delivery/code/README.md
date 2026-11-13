# 固定 HTTPS 验证入口与实际参数

站点源码 `70ef503fc2fb8b2c787fa9065e2952f525c40099` 中的
[CoreS3 runner](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_qemu_guest.mjs)
执行 `stock-reference` 和 `wallclock-candidate`。与本地 runner 相同，但删除 `M5_PUBLIC_SITE`，
通过公开 `M5_PUBLIC_URL` 加载真实部署，并用完整 HTTPS 字节读回作为前提。

实际 Node 为 `22.14.0`；固定 package-lock 锁定 Playwright/Playwright Core `1.64.1`。
本轮使用 Chrome `157.0.8103.52`，exe SHA 见[浏览器收据](../evidence/https-browser-provenance-summary.json)。
下面是实际命令参数的可重放形式；复现者提供独立 checkout、匹配 Chrome 和全新输出目录：

```sh
# 从固定源码 checkout 根目录执行；PAGES_CHROME 和 PAGES_OUTPUT 由复现者设置。
python3 - <<'PYCODE'
from pathlib import Path
import os, subprocess, hashlib
source = Path.cwd()
chrome = Path(os.environ['PAGES_CHROME']).resolve()
out = Path(os.environ['PAGES_OUTPUT']).resolve()
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == '70ef503fc2fb8b2c787fa9065e2952f525c40099'
assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], text=True)
assert hashlib.sha256(chrome.read_bytes()).hexdigest() == '5441ca699b9eff7763f2f10765e2e8409a4b05f38917826b5247f6f6bb3b0c6b'
out.mkdir(parents=True, exist_ok=False)
env = {k: v for k, v in os.environ.items() if not k.startswith('M5_')}
env.update(NODE_PATH=str(source/'platform/tests/node_modules'),
           M5_PUBLIC_URL='https://m5agent.github.io/m5stack-esp-emulator/',
           M5_PUBLIC_BASE_PATH='/m5stack-esp-emulator/', M5_WASM_GPU='hardware',
           M5_WASM_CHROME=str(chrome), M5_CHROME=str(chrome),
           PLAYWRIGHT_CHROMIUM_EXECUTABLE=str(chrome), M5_QEMU_READY_TIMEOUT_MS='600000',
           M5_QEMU_GATE_REQUIRE_ALL='1', M5_QEMU_GATE_WORKERS='1',
           M5_QEMU_GATE_PHASE='all', M5_QEMU_GATE_DEVICES='')
for example in ('stock-reference', 'wallclock-candidate'):
    with (out/(example+'.log')).open('xb') as log:
        subprocess.run(['node', str(source/'platform/tests/test_public_qemu_guest.mjs')],
                       cwd=source, env={**env, 'M5_QEMU_EXAMPLE': example,
                       'M5_PUBLIC_QEMU_OUT': str(out/example)},
                       stdout=log, stderr=subprocess.STDOUT, check=True)
assert hashlib.sha256(chrome.read_bytes()).hexdigest() == '5441ca699b9eff7763f2f10765e2e8409a4b05f38917826b5247f6f6bb3b0c6b'
PYCODE
```

复现前应取得站点 manifest 与全部文件，按每项 bytes/SHA 核对资格清单，并检查读回前后和 guest
前后的 manifest 仍为 `54fc8d8fe023ef0d86e3bfdea3d3db37599a2f59404c54fdb8920d466bd14a8c`。
实际包装流程还保存 before/after 的源码/导出/Chrome 身份与 20 次采样，以及 2 个 child 的 SHA 闭集；
只有上述命令成功不能代替这些来源检查。公开站点将来可能变化，新执行应单独形成记录。

发布入口为固定源码
[prepared workflow](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/.github/workflows/public-site-prepared-preview.yml)，
实际 run ID 与输入 tag 见[发布收据](../evidence/workflow-deployment-summary.json)。
该 workflow 没有重新执行 hosted 完整 72 例。复现不得替换 guest oracle、缩短观测、隐藏失败或以 native session 代替 HTTPS。
