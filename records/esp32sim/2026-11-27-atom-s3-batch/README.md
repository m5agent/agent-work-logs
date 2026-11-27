# AtomS3 native simulator batch

2026-11-27 · PARTIAL · virtual-device validation

AtomS3U and Atom VoiceS3R each passed all five pinned Arduino cases and the
stock UIFlow2 v2.5.4 USB CDC board-ID and button checks. The same native
binary ran both matrices. The first long AtomS3U button runs reached the
host wall timeout. Shorter runs repeated both button transitions and the
idle control and exited normally.

- [Milestone source](https://github.com/m5agent/esp32sim/tree/de2292fc48d35a8418c398bc7cae003e3796db78)
- [Replay and observed results](report.md)
- [Run manifest](run.json)
- [Per-image hashes and checker outputs](evidence/milestone-summary.json)
