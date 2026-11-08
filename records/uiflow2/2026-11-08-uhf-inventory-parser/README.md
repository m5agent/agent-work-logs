# UIFlow UHF inventory parser validation

On 2026-11-08, DeepSeek executed 35 virtual-device sessions. The final source overlay passed all nine declared UART vectors. The original baseline retained four failures and the original maintainer candidate retained three. Overall status is PARTIAL while maintainer review and merge are pending.

The work covers issue handling, a two-method code change and virtual-device validation. The base is public UIFlow source `f20d5a00e8c9106aae1d944f3d6f1128839f59cb`. CoreS3 public v2.5.5 preview exercised the shared UART parser path as the substitute for Core2.

- [Report, matrix and limits](report.md)
- [Structured run](run.json)
- [Public-base patch](patches/0001-fix-uhf-frame-parser.patch)
- [Independent receipts](evidence/independent-receipts.summary.json)
- [Executor completion](evidence/executor-completion.summary.json)
- [Exact executed probes](evidence/probe-inventory.summary.json)
- [Fixture generator](code/generate-fixtures.py)

`evidence/` contains derived, redacted summaries. Full synthetic values, raw serial responses, infrastructure identifiers and private endpoints are omitted. `code/probes/` contains the 35 exact executed VFS main scripts. Fixture construction rules and hashes allow synthetic inputs to be regenerated.

Original Core2 and 2.4.3 binary execution, physical RF/electrical properties, timed same-response fragmentation, other command decoders and long-duration behavior are NOT RUN. The final turn completed normally and all 35 histories were retained.
