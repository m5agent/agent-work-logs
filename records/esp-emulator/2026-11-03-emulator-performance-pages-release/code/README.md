# Frozen HTTPS adapter source restoration

This bundle restores the exact fifteen-member adapter identity used for the reviewed Pages HTTPS path. It does not execute a browser, guest, network request or build. Do not describe the newly generated files as a newly executed online harness.

Use the fixed source checkout `10788607feefb9e532c2dd1fe4679adcd6aa0fc2`. Its tree and all six parent source files are byte-identical to the adapter's original declared source `1b86ed6f7edcc36deafc4834b45a28c6a6017c79`; the original identity JSON is retained unchanged, not relabeled.

## Restore

Set `$SOURCE_ROOT` to a new independent source checkout, and `$RECORD_ROOT` to this record directory. Do not use an existing execution checkout. The restorer refuses the wrong commit, a dirty tracked tree, a shared/symlinked work directory or an existing adapter output.

```bash
git clone https://github.com/m5agent/m5stack-esp-emulator "$SOURCE_ROOT"
git -C "$SOURCE_ROOT" checkout --detach 10788607feefb9e532c2dd1fe4679adcd6aa0fc2
python3 "$RECORD_ROOT/code/restore_adapter.py" --repo "$SOURCE_ROOT"
npm ci --prefix "$SOURCE_ROOT/platform/tests"
```

The original `prepare.py` generator copies four unchanged helpers from the fixed repository and generates two HTTPS-only runners plus their two transport deltas. Seven frozen non-generated seed members are distributed, including the original source/archive preflight, metadata label delta and offline control source. The resulting fifteen files and `adapter-identity.json` must match the manifest exactly; identity SHA-256 is `ecc887184178b99656bdada419502355940ee6cec7ec45a405c2259a822efa87`.

The source package does not distribute the old README, bytecode, raw reports, runtime/ROM/firmware or removed local-server diff context. The original generator recreates the latter from public test source. All source retains the repository MIT license, included as `LICENSE`.

## Required release pins

The transport accepts only `https://m5agent.github.io/m5stack-esp-emulator/`, requires all four explicit SHA-256 pins, rejects redirects, verifies actual fetched bytes and source/archive closure, and checks the running guest receipt. There is no local fallback, clock override or guest-state substitution.

```bash
export M5_PAGES_MANIFEST_SHA256=c5991d737d4b20c4b1ae96b71587cec907a1e72f3c57fe2fee63c08e23daf323
export M5_PAGES_RUNTIME_SHA256=897114f09d5e0c695e44e665611fec4fa98aa62856cddce6eb1cbb906d21071c
export M5_PAGES_WASM_SHA256=3c6b249002d83118e0ddcbd82e4ee6336223293b98566fc7709d5087d9df4567
export M5_PAGES_SOURCE_LOCK_SHA256=b9b137e52e77078cc67cb5b25433622f62d70cc3cbed8f92ee6699eed3389a1b
```

The pins identify the reviewed prepared export. A later online version must fail these pins rather than silently selecting different assets.

## Explicit reproduction commands

Run from `$SOURCE_ROOT`. Set `$CHROME_EXECUTABLE` to a real supported Chrome with a hardware renderer, `$STACKCHAN_DANCE_BIN` to the independently obtained exact dance full-flash input, and each output variable to a fresh location under the checkout's ignored work directory. No binary is bundled here. Raw outputs can contain environment paths and IDs; do not publish them directly.

Remote artifact/source verification only, with no browser or guest:

```bash
M5_PUBLIC_URL=https://m5agent.github.io/m5stack-esp-emulator/ \
M5_PAGES_PREFLIGHT_OUT="$PREFLIGHT_OUTPUT" \
node .work/pages-remote-tools/preflight.mjs
```

Public StackChan reference guest, real UI/controller/frame/cleanup:

```bash
M5_PUBLIC_URL=https://m5agent.github.io/m5stack-esp-emulator/ \
M5_PUBLIC_BASE_PATH=/m5stack-esp-emulator/ M5_PUBLIC_UI=1 \
M5_QEMU_DEVICE=stackchan M5_WASM_GPU=hardware M5_WASM_CHROME="$CHROME_EXECUTABLE" \
M5_PUBLIC_QEMU_OUT="$REFERENCE_OUTPUT" \
node .work/pages-remote-tools/board_guest.mjs
```

Exact dance firmware cold/repeated twenty-second observation:

```bash
M5_BENCH_URL=https://m5agent.github.io/m5stack-esp-emulator/ \
M5_BENCH_ENGINE=qemu M5_BENCH_DEVICE=stackchan M5_BENCH_SOURCE=local \
M5_BENCH_IMAGE="$STACKCHAN_DANCE_BIN" \
M5_BENCH_IMAGE_SHA256=c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542 \
M5_BENCH_SAMPLE_MS=20000 M5_BENCH_RUNS=2 M5_BENCH_REQUIRE_RENDERED_MOTION=1 \
M5_WASM_CHROME="$CHROME_EXECUTABLE" M5_BENCH_OUT="$DANCE_OUTPUT" \
node .work/pages-remote-tools/benchmark.mjs
```

For the independent eight-second input protocol, keep the same image, URL, four pins and other options, use a fresh `$TOUCH_OUTPUT`, change `M5_BENCH_SAMPLE_MS=8000`, `M5_BENCH_RUNS=1`, add `M5_BENCH_INPUT=known-device-controls` and set `M5_BENCH_OUT="$TOUCH_OUTPUT"`. The original runner restricts these two protocols and requires actual rendered motion.

## Evidence boundary

`restoration-proof-summary.json` proves source generation and relative imports only. It does not run the restored adapters or the included offline controls. The historical `test_remote_release.mjs` additionally needs a separately retained historical runtime fixture, which is intentionally not bundled. The actual online report must bind all fifteen original member hashes and separately prove strict release pins, serial, inputs, frames/render and normal target cleanup.
