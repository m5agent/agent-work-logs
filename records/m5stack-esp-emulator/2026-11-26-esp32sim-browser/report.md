# esp32sim browser-WASM validation

## Scope

The hosted documents embed issue concerns QEMU-WASM shared-memory admission. The new source export defaults to current esp32sim for CoreS3 and Cardputer-ADV. A frozen QEMU-WASM engine remains available in mixed exports. PaperS3 and StopWatch retain their separately rebuilt esp-online-tester pin.

## Reproduction

Build with `python3 platform/tools/bootstrap_browser_runtime.py --fetch-rom` and export with `python3 platform/tools/build_public_site.py --output .work/browser-site --browser-runtime .work/browser-runtime`. Serve the static output on a dedicated test port and run `platform/tests/test_public_esp32sim_guest.mjs` using the documented firmware inputs. Optional legacy and QEMU bundles exercise their independent paths.

- esp32sim source `25c3948c8311f5afe95d6058add3d2c298e75c4b`
- WASM SHA-256 `ecbf5810ec8ecef331e02b5128e0a1e7bae8ebe9c94dbd36330c7f75d3f22e0c`
- S3 ROM SHA-256 `c0ce0f338d1de1bdc6efbef1591779a2a42c1ab7d759d3c6ae8ae63a7dd34cfd`

## Results

- cores3 display passed with input SHA-256 `a88182dc789c1dfe7525ad7ff9a284fd201b6c55375502c895b689cd56af13d6`.
- cores3 touch passed with input SHA-256 `3cec5642f681dc0525c7e6cdbada7189f0ee52f9a95b68b19055571664222606`.
- cardputer-adv keyboard passed with input SHA-256 `f7edb36bb3662506853773399467841a55bef3d3e16cc3469bc821b4ad7638bf`.
- cores3 uiflow passed with input SHA-256 `1324f12d3ddd5392f47a9eff537f9ce0b01a8e6e36d829b6bd22cdf82d2c1264`.
- stopwatch legacy passed with input SHA-256 `6395799089341e0ae96072c2a3418d469d6797b2ab8ee0cab1c9ed24a42acbbe`.
- cardputer-adv display passed with input SHA-256 `cc1b3e5868feb075e2ec8a5e7211897e8ae1c9635f5d072442ef007273c2a968`.
- cardputer-adv button passed with input SHA-256 `07ebcecd82c9a64aad457f5e30eac140bfd24db8006506ea6f04489a860dc0e7`.
- papers3 legacy passed with input SHA-256 `d6733a0ca378f95335fa5fba4d4d992fb1dd97c17557b20e9aebfca08ba6d624`.

CoreS3 Touch rendered coordinates (113, 95) from a transformed model touch. The UIFlow2 Home tap (34, 47) opened Settings and produced PCM chunks plus WebAudio buffer sources. The separate CoreS3 Button sketch redrew after a PMIC power press from the device page. ADV typed characters reached its keyboard sketch through TCA8418 and appeared as `ab`. The ADV Button guest reported both G0 edges over serial. Every passing case recorded one dedicated Worker before Stop and zero after Stop while the iframe or device page remained open.

Earlier screenshot waits expired on three attempts after guest output was observed. The runnable capture probe now avoids waiting for a static element during continuous updates. Those records remain separate from passing reruns. The summary omits URLs, console payloads, identifiers and raw screenshot bytes, and retains source transcript hashes and byte counts.

The QEMU-WASM engine menu reached the isolated workbench. QEMU guest regression, hosted rollout, physical hardware and the complete browser firmware matrix remain outside this local run. Browser networking, external Unit attachment and persistent Flash were outside this integration.

## Stock reference follow-up

The direct reference download reached a visible CoreS3 UIFlow2 v2.5.3 screen.
The ADV v2.5.3 reference passed SHA admission and produced black frames. An independent
native check on the identical ADV input logged an uninitialized I²C port and observed zero
SPI3 LCD bytes in six virtual seconds. The workbench and ADV device page now show this
limitation when using esp32sim.
[Evidence and exact hashes](evidence/stock-reference-followup-summary.json)
