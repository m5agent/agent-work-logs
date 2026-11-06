# Historical extraction backlog — batch 01

- Date: `2026-11-06` (`Asia/Shanghai`)
- Result: `PASS` — audited historical coverage and extraction fidelity.
- Source: [OpenViking `v0.5.3`](https://github.com/volcengine/OpenViking/tree/v0.5.3)

## Result

New recovery covers **49,420 source messages across 18 historical sessions**. Together with 35,815 natively completed messages and the prior 10-message recovery, all **85,245 original failed-archive message IDs** are covered, with zero pending IDs. All 184 original archive hashes remain unchanged, and the protected 28-message retained/live set has zero replay overlap.

The auxiliary-artifact omission was corrected: all 786 affected contexts completed faithful corrective extraction, and 3,476 artifact file/API hashes matched. The sealed 67-message supplement had its 13 external references present before extraction. One failed corrective attempt is retained and fully superseded by four completed successors; no completion marker was fabricated.

## Evidence

- [Final independent audit](evidence/final-combined-fidelity-audit-summary.json): source coverage, artifact fidelity, successor lineage, 42 current canonical targets, and five quarantined artifacts.
- [Main import audit](evidence/main-import-coverage-summary.json): 104 completed main tasks and 49,353 exact imported contexts.
- [Native managed-link review](evidence/managed-link-independent-review-summary.json): the earlier diff mismatch is explained by 14 native managed relations.
- [Scoped semantic retrieval](evidence/semantic-retrieval-summary.json): two newly created targets were indexed and retrieved, one global and one project-scoped.
- [Post-audit health](evidence/final-health-summary.json): HTTP 200, healthy version 0.5.3.
- [report.md](report.md), [run.json](run.json), and [provenance](evidence/provenance-summary.json).

## Limits

Message coverage does not mean one new memory per message. Recorded operations are not net memory-file growth. Earlier partial/failure snapshots remain as historical evidence. Semantic retrieval was a scoped sample, not a ranking benchmark. Final readiness was not retested. The separate 120-second startup recall-compressor path was unchanged and is outside this result.
