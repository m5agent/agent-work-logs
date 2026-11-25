# Cardputer-Adv Button private icount comparison

Virtual-device validation on the sealed 0046 browser WASM and exact original Arduino Button image. Three fresh Chrome runs selected a private `tcg,thread=single,tb-size=128` profile with `-icount shift=5,align=off,sleep=off`. The standard workbench JavaScript and firmware were byte-identical to the canonical test inputs.

All three guests reached ROM handoff and produced frames. Both G0 inputs received QMP acknowledgments. The public USB Serial/JTAG panel and controller output showed `Button A Released` after keyup in each run. `Button A Pressed` was absent throughout each 20-second F12 hold. The error handler stopped each guest through the same runtime teardown path. Exit code was 0, the iframe was removed and all five dedicated Worker targets disappeared before context closure.

This profile yielded **0/3** complete cold starts. The prior default batch was **3/5** and the prior interleaved comparison was **2/3** for both default and one-instruction-per-TB. Keep the batches distinct. The single-thread diagnostic does not provide a workaround for the original Button demo. The available observations do not determine which guest or controller stage lost the press output.

The [bounded summary](evidence/button-0046-icount.summary.json) contains exact identities, the raw report hashes and per-run observations. The raw browser reports and screenshots remain in the ignored work directory.

## Replay in the same fixture checkout

Use the sealed 0046 export, original docs fixture and ROM paths pinned in the private harness. The sealer creates a fresh sibling `private-button-icount-0046-site` and rejects an existing destination. Copy the three archived scripts from `code/` into the isolated `icount-diagnostic` workspace path. Run from the repository root with the existing Playwright and Chromium setup.

```sh
lab=.work/docs-wasm-cardputer-adv-usb-lab/icount-diagnostic
python3 "$lab/seal-button-icount-0046.py"
node "$lab/run-button-icount-0046.mjs" "$lab/private-button-icount-0046-site" preflight "$lab/preflight-unused"
for i in 1 2 3; do
  node "$lab/run-button-icount-0046.mjs" "$lab/private-button-icount-0046-site" on "$lab/browser-button-0046-icount-cold-$i" || true
done
python3 "$lab/summarize-button-icount.py"
```
