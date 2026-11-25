# CoreS3 UIFlow2 Blockly source preview

- Date `2026-11-25`
- Result `PARTIAL`
- Work type `issue`
- Source [Emulator issue #255](https://github.com/m5agent/m5stack-esp-emulator/issues/255), official UIFlow2 SDK examples and the [UiFlow2 editor](https://uiflow2.m5stack.com/)
- Source revisions `73696ca95594646f09a39e4f525b20cf5cc550e5` for DualKmeter and ModuleLLM, `a61a29409f09f1f4bebae05e15c4bd6dcc4956b6` for Arc and Switch
- Environment Chromium `158.0.8127.37`, official UIFlow2 editor `V2.5.5`; editor generation and static driver inspection

## Result

The official UIFlow2 editor generated full Python for both original CoreS3 projects, DualKmeter and ModuleLLM voice assistant. Independent offline sessions using the same verified editor assets produced byte-identical results. The locked default WASM workbench ran the exact output from each import. DualKmeter stopped at its I2C ready check, and ModuleLLM displayed its connection-wait screen for 35 seconds. The corresponding MBUS I2C and UART module attachments remain missing from the current public browser simulator.

The shipped M5Arc Blockly and Python assets are copies of their M5Switch counterparts. Re-importing the exact Blockly file into UIFlow2 `V2.5.5` hit an invalid legacy Switch block. The partial preview still emitted `M5Switch`. A replacement Arc example requires the correct project and a value-change test.

## Files

- [Report and reproduction steps](report.md)
- [Structured result](run.json)
- [Editor, project and generated source digests](evidence/source-provenance.summary.json)
- [Arc and Switch duplicate assets and legacy-import evidence](evidence/arc-upstream.summary.json)
- [Same-source Switch browser guest, touch and cleanup](evidence/same-source-switch.summary.json)
- [Both generated programs in default browser WASM](evidence/browser-baseline.summary.json)

## Remaining checks

Positive DualKmeter and ModuleLLM browser qualification requires their corresponding attachments. Physical modules, sensor readings and raw speech processing were outside this execution. The linked Arc files contain no Arc program to execute. [Upstream M5Arc issue #133](https://github.com/m5stack/uiflow-micropython/issues/133)
