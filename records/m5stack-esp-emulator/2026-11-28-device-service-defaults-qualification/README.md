# Device Service default migration qualification

- Date `2026-11-28`
- Result `PARTIAL`
- Work type `code_change`
- Prior qualification [Device Service board-state and routing candidate](../2026-11-27-device-state-routing-candidate/)
- Service candidate `872c92e18408696c1a12f4c5a9ed5db119f18adf`
- Fork candidate `4245d96b1cf3fae5c2360a87cd6b716bc1c94c9d`
- Environment macOS arm64, isolated native Device Service and saved-snapshot reviewer, virtual-device validation

The shared oracle passed 56/56 cases on esp32sim and 47/56 on QEMU in each of two trials. All 224 leases completed cleanup. The paired StopWatch PM1, StickS3 peripherals and StackChan legacy touch fixtures now pass. Tab5's original UserDemo exposes a live stereo cursor and a retained audio window. The saved Tab5 frame review still fails on esp32sim because it requires the legacy post-touch frame digest. The qualification branches are available for continued work. The default and resident cutover gate remains open.

## Files

- [Report and per-device table](report.md)
- [Structured run record](run.json)
- [Shared oracle evidence](evidence/shared-oracle-summary.json)
- [Paired fixtures and guest markers](evidence/paired-fixture-summary.json)
- [Reviewer job results](evidence/reviewer-summary.json)
- [Nesso N1 guest BQ27220 register probe](code/main/probe.c)

## Limits

The Tab5 25-case standalone gate, additional paired board fixtures and several reviewer endpoints remain open. Physical hardware, deployment and resident rollback were outside this isolated execution.
