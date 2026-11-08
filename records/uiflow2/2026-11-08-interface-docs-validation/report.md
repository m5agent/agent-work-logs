# UIFlow2 Display, ADC and m5ui documentation correction

## Target and source boundaries

The target is accurate, executable documentation for Display parameter requirements, the ESP32 ADC API and the m5ui homepage example. The public patch applies to [f20d5a00e8c9106aae1d944f3d6f1128839f59cb](https://github.com/m5stack/uiflow-micropython/tree/f20d5a00e8c9106aae1d944f3d6f1128839f59cb) and changes six English RST/Chinese PO files, +485/-143 lines. It changes documentation and example code only.

The validation source snapshot is referred to as `validation-source-A`. Its relevant 29 native Display C functions match the pinned public source after whitespace normalization. [The bounded equivalence summary](evidence/public-contract-equivalence-summary.json) records that scope. The equality proof covers the listed functions and files. The public source anchors are [Display binding](https://github.com/m5stack/uiflow-micropython/blob/f20d5a00e8c9106aae1d944f3d6f1128839f59cb/m5stack/components/M5Unified/mpy_m5gfx.cpp), [hardware import namespace](https://github.com/m5stack/uiflow-micropython/blob/f20d5a00e8c9106aae1d944f3d6f1128839f59cb/m5stack/libs/hardware/__init__.py), and [m5ui port](https://github.com/m5stack/uiflow-micropython/blob/f20d5a00e8c9106aae1d944f3d6f1128839f59cb/m5stack/libs/m5ui/port.py).

## Diagnosis and changes

A Display initializer inside a C binding argument table does not make an `MP_ARG_REQUIRED` parameter optional. The patch corrects 90 misleading required-parameter default annotations and makes 50 optional parameter defaults explicit. The 29 affected methods are a subset of 43 keyword bindings and the 99 actual omission checks are distinct from the 90 edited annotations. Omitted drawing color uses the current drawing color through the binding's `-1` sentinel. `setTextColor` still requires foreground color and has optional background color.

The ADC example uses the actual `hardware`/`machine` namespace and `Pin` and constructor attenuation may be omitted, with the pinned ESP32 implementation selecting `ATTN_11DB` (numeric 3). Each method is independently guarded so an unsupported calibrated read does not suppress raw/u16 or setter observations. The docs explain the possibility of `OSError` from calibrated readings and calibration availability remains port-dependent.

For m5ui, source inspection and fresh-guest behavior refute the initial assumption that callers must always invoke `M5.begin()` themselves. `m5ui.init()` already initializes M5 internally. The revised example calls `M5.begin()` explicitly to set rotation before LVGL initialization and calls `page0.screen_load()` to make the page visible. The optional font falls back to an available font. The exact revised example was executed with only bounded observation code appended.

## Runtime and firmware provenance

All five runs used fresh CoreS3 virtual-device sessions through the Device Service `/api/v1` API. The native runtime binary SHA256 is `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`, profile SHA256 `3e88ec4dd64da5f5dc4a5bc2b8c79fe19e047ee23dd075709a97798c28e6347e`, emulator source commit `dd2eb35d2e6a909992268089ddc37e27970d4a92`. No direct runner bypass was used.

The official public UIFlow2 CoreS3 v2.5.5 **preview** base is 16,121,856 bytes, SHA256 `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded`. Flash is padded with `0xff` to 16,777,216 bytes for comparison. Caller probes, dupterm boot bridge and explicit fixtures were composed into the VFS at offset 11,141,120, size 4,980,736. Independent comparison verified all non-VFS bytes, including the native application partition, unchanged and mounted LittleFS readback verified the actual probe and boot bytes and preservation of unrelated files. Execution uses the existing native application with the stated VFS probe files.

For each run, [session receipts](evidence/session-receipts-summary.json) retain aliases, exact probe/composed-firmware/runtime/frame/ZIP hashes, 19 independent receipt predicates and the seven indexed ZIP member sizes/hashes. All 35 member checks passed. Independently sampled live process identity matched the observed runtime binary and this goes beyond reading runtime configuration alone. API and ZIP frame pixels agreed. The owned session was stopped after evidence collection with history retained and no purge. Original host paths, endpoints and unique session/process identifiers are intentionally absent from the public summary. Mutable full flash after execution was not independently read back and the image comparison concerns retained composed inputs.

## Actual results

| Run alias | Actual observations | Verdict and boundary |
| --- | --- | --- |
| `display` | 29 methods and 99 exact expected `TypeError` omissions and 58 normal returns and 159 total marker rows | `PASS` signature/accepted-call contract and four selected frame groups and full method functionality not established |
| `adc` | Both namespaces identical and 6 constructors/default/setters and each raw=2048 and u16=32776 and 6 independent `read_uv()` errors | `PASS` imports/default/raw/u16 and calibrated UV `PARTIAL`, error 95 cause not localized |
| `m5ui-auto` | No explicit caller `M5.begin()` and state `[0,320,240]` and LVGL `[320,240]` and Title/Text/123 read back and visible | `PASS` automatic initialization and visible labels |
| `m5ui-explicit` | Rotation1 before/after init `[1,240,320]` and LVGL `[240,320]` and labels correct | `PASS` state, `PARTIAL` framebuffer: API capture remains320x240 with right80x240 black stripe |
| `m5ui-example` | Exact revised candidate prefix and rotation0, 320x240 and all three labels correct/visible | `PASS` exact revised example, frame pixel-identical to auto-init run |

Display frame predicates independently checked 4,000 blue rectangle pixels, red explicit/inherited-color adjacent pixels, green circle cardinal points with white center, and visible black `DOC27` text (61 dark pixels in the checked text region). The normal-return calls establish argument handling. Broader rendering, codec, e-paper and physical-brightness validation remains outside this record.

ADC's omitted and explicit11DB constructor repr is `ADC(Pin(6), atten=3)` and explicit0DB repr is `atten=0` and each subsequent setter reaches3. Raw2048 maps to32776 by `(2048 << 4) | (2048 >> 8)`. These values describe the current default virtual-controller input. Calibrated voltage and analog transfer-curve validation remain unestablished. Each `read_uv()` independently returned `OSError(95, 'ESP_ERR_NOT_SUPPORTED')`. The cause could not be localized by these traces and virtual eFuse state or firmware calibration configuration is not asserted as the root cause.

The rotation1 capture's first240 columns match the corresponding auto-init crop pixel for pixel and the remaining80x240 area is black (19,200 pixels). This supports visible labels and correct logical rotation/size, but does not establish a complete240x320 portrait surface. No model-specific root cause is inferred from this result.

## Execution history and static checks

The first host wrapper omitted the runner's module directory from its import search path and failed with `ModuleNotFoundError: No module named 'run_guest'` before any service POST or guest creation. Correcting the host wrapper enabled the five actual runs. An expanded14-method Display scratch probe was prepared but never run and it is excluded from all executed counts.

Each runner returned0 and reported `EXECUTED`. The marker observations, independent source/VFS/runtime/ZIP checks, image predicates and honest limits above determine the conclusions. The independent snapshot predates the final DeepSeek executor turn. The [coordinator completion receipt](evidence/executor-completion-summary.json) confirms normal completion and rechecks each owned history and runtime exit.

Static validation compiled54 inline Python blocks, parsed the three related Chinese PO files, checked66 newly nonempty Chinese translations and six generated HTML pages, and produced exit0 in final English and Chinese Sphinx builds with no new warnings. The first full Chinese build showed eight unrelated PO syntax-warning files and each was already invalid in the baseline and unchanged. They remain outside this patch. The final incremental result must not be read as repair of those baseline files. [Detailed summary](evidence/documentation-checks-summary.json).

## Reproduction

Apply the patch to the pinned public base with `git apply --check` before `git apply`. [Application evidence](evidence/public-patch-application-summary.json) records all six base/result byte hashes. Native application code does not change. Use the [exact probes and fixtures](code/README.md), the stated preview base hash and runtime hash, create a fresh session for every probe, collect the serial markers and frame, then stop the owned session while retaining history.

At the pinned emulator source, the existing session client accepts this command pattern (environment values are operator supplied and they are not captured endpoints):

```sh
python3 tests/uiflow2/api_sweep/run_guest.py \
  --api "$DEVICE_SERVICE_ORIGIN" --token-file "$DEVICE_SERVICE_AUTH_FILE" \
  --device cores3 --runtime qemu \
  --base-image "$UIFLOW2_CORES3_PREVIEW_BIN" \
  --expected-base-sha256 5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded \
  --uart-repl-bootstrap dupterm \
  --source "$RECORD/code/display.py" --fixture-dir "$RECORD/code/fixtures" \
  --out-dir "$RUN_OUTPUT/display" --done-marker "DOC_TOP3_DONE DISPLAY" \
  --timeout 120 --prepare-timeout 600 --ready-timeout 60
```

The client creates visible sessions through the service API. Substitute each probe/marker as listed in [code/README.md](code/README.md), always with a fresh guest. Re-check the independent predicates rather than accepting return0 alone.

## Limits, delivery and rollback

Coverage marked `NOT RUN` includes other14 keyword bindings, full29-method graphics functionality, multi-voltage response, calibrated analog accuracy and physical properties. Coverage marked `PARTIAL` includes calibrated UV capability and full portrait-frame capture. The patch is a documentation correction and rollback reverses the six-file patch. The coordinator completion evidence accompanies this record. Upstream review remains a separate delivery step.

## Record correction

The public patch line count is +485/-143 according to `git apply --numstat`. The earlier record used the review-snapshot totals of +484/-144. Public patch SHA256 is `189798430297d06c8cf16e3019a6ba3ddb241bbd5d9861578c99fb75176160a0`.
