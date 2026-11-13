# Tab5 original firmware on esp-emu v1.0.0

- Date: `2026-11-14` (UTC+08:00).
- Type: original-firmware regression and upstream-runtime evaluation.
- Result: **FAIL** for both original applications; test execution and cleanup **PASS**.
- Issues: [#188](https://github.com/m5agent/m5stack-esp-emulator/issues/188) and [#226](https://github.com/m5agent/m5stack-esp-emulator/issues/226).
- Source: [a5990e720a8c79310456bf5868141f4cfd50afe8](https://github.com/m5agent/m5stack-esp-emulator/commit/a5990e720a8c79310456bf5868141f4cfd50afe8).
- Validation: native **virtual-device validation**, using normal Device Service upload, import, session and evidence APIs. Physical hardware and browser-WASM were not run.

The stable upstream executable differs from the previously tested rc2 binary,
so both original images were tested again. UIFlow2 V2.5.4 repeatedly faulted
while reading the older P4 interrupt CSR. Maker Fighter 1.4 also faulted at
this earlier startup stage: its missing USB assertion in this run does **not**
mean USB was repaired. Neither application became ready, and neither issue
is closed by this evaluation.

| Original image | Window | ROM boots | Fault instruction occurrences | Application |
| --- | ---: | ---: | ---: | --- |
| UIFlow2 V2.5.4 | 120.909 s | 134 | 133 | FAIL; no MicroPython banner |
| Maker Fighter 1.4 | 60.516 s | 80 | 79 | FAIL; USB stage not reached |

The exact original app partitions were preserved. Each run retained a valid
four-file evidence ZIP before stop, released Flash and lease, and verified
termination of both original P4/C6 processes and its dedicated service.

[Report](report.md), [structured record](run.json),
[UIFlow2 execution](evidence/issue188-execution-summary.json),
[Maker Fighter execution](evidence/issue226-execution-summary.json),
[independent audit](evidence/independent-audit-summary.json),
[offline analyzer](code/analyze_serial.py) and its
[same-log check](evidence/offline-analyzer-summary.json).

No runtime source repair, deployment, issue comment, issue closure or Burner
submission was performed by these trials. Runtime binaries, original firmware,
raw serial, mutable Flash, process identities and local service information
are omitted; the summaries retain their hashes and bounded observations.
