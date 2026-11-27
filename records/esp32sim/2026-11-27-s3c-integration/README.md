# S3-C fork integration

S3-C landed in [esp32sim at `d992a117`](https://github.com/m5agent/esp32sim/commit/d992a1171db4aed2504603fa3fa91b259be2fca4). The annotated milestone is [`m5-milestone-s3c-20261127`](https://github.com/m5agent/esp32sim/releases/tag/m5-milestone-s3c-20261127).

Native virtual-device validation passed all runnable cases and the stock UIFlow2 profiles for StamPLC and StackChan. The workspace passed 1995 tests. CoreS3 and Cardputer-ADV retained 15/15 and 11/11, and both ADV CAP NFC cases reproduced 33 selections.

- [Report](report.md)
- [Runtime and firmware hashes](run.json)
- [Per-case gate outcomes](evidence/gate-summary.json)
- [Instruction sentinels](evidence/instruction-sentinels-summary.txt)
