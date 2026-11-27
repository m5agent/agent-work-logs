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

## Batch follow-up

22 of 25 Arduino cases passed. Three cases expose documentation defects
in the original AtomS3 serial examples. All seven factory UIFlow2 catalog
images passed stock console and input validation. The follow-up records
both native regression matrices, source and binary identities, and the
remaining model limits.

- [Full batch report](batch-follow-up.md)
- [Replay summaries](evidence/atom-s3-replays-summary.json)
- [Regression summary](evidence/atom-s3-regression-summary.json)
