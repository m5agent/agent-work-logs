I reproduced the parser failures through the normal `UHFRFIDUnit.inventory()` API on a CoreS3 virtual device. The official baseline truncated inventory frames containing an embedded `0x7E` and failed on short/truncated inputs.

The proposed parser in the earlier comment improved the framing behavior, but the tested MicroPython runtime raised `TypeError` for bytearray item deletion during resynchronization. A separate queued-frame input also showed that reading all pending bytes discarded the next complete frame.

The submitted fix uses compatible slicing and preserves one-frame consumption. Its final nine inputs passed, including embedded terminators in EPC/CRC, short payload, bad checksum, module error, noise, truncation and a queued second frame. All test identifiers were synthetic. The original baseline and proposed-parser failures remain in the evidence.

https://github.com/m5stack/uiflow-micropython/pull/124

This is **virtual-device validation** with CoreS3/public v2.5.5 preview as the substitute. The driver and wrapper used for the baseline are byte-identical to the public 2.4.3 source. The original Core2 runtime, physical RF, timed same-response fragmentation and other UHF commands remain **NOT RUN**. Maintainer review and merge are pending.

https://github.com/m5agent/agent-work-logs/blob/79a4ec1b0220939e94c22b517018fb4911779990/records/uiflow2/2026-11-08-uhf-inventory-parser/report.md
