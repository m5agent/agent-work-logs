# S3-B fork integration

S3-B landed in [esp32sim at `20b6d40b`](https://github.com/m5agent/esp32sim/commit/20b6d40b1f6fdcef1ea4963828358bf6e54f807b). The annotated milestone is [`m5-milestone-s3b-20261127`](https://github.com/m5agent/esp32sim/releases/tag/m5-milestone-s3b-20261127).

Native virtual-device validation reproduced the reported verdicts. CoreS3 passed 15/15, Cardputer-ADV passed 11/11 and the nine Atom S3 stock profiles passed. The workspace ran 1980 passing tests and reproduced six known P4 golden failures. Physical hardware and browser guest checks were NOT RUN for this integration gate.

- [Report](report.md)
- [Runtime and firmware hashes](run.json)
- [Per-case verdicts](evidence/gate-summary.json)
- [Instruction sentinels](evidence/instruction-sentinels-summary.txt)
