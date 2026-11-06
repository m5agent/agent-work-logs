# Historical extraction backlog recovery — final report

## Outcome and scope

`PASS` for recovery of the selected historical backlog and faithful extraction input/output handling on OpenViking `v0.5.3`. The final independent audit certifies 49,420 newly recovered source messages across 18 historical sessions. Combined coverage is:

| Coverage source | Unique source-message IDs |
| --- | ---: |
| Previously completed natively |35,815 |
| Prior verified scoped recovery |10 |
| New main recovery |49,353 |
| Sealed supplemental recovery |67 |
| **Total original failed-archive coverage** |**85,245** |
| Pending |**0** |

All 184 original source archive hashes remain unchanged. None of the 28 protected retained/live message IDs overlap recovery. The 786 visibility-correction contexts are repeated extraction context required to repair input fidelity, and are not additional unique primary recovery IDs.

## Execution and validation

The main frozen plan completed 104 chunks. A separate 67-message supplement completed one chunk after a source/marker/hash assessment proved it was sealed before the backlog request and disjoint from retained/live messages. The main plan and its protections were not weakened to add this supplement.

Seven helper contract tests passed, including source/snapshot mutation rejection before writes, literal Unicode/LF handling, recovery after lost write responses without duplicate POSTs, and conservative retry selection. A wrapper stop-control fixture preserved completed results and did not report unattempted work as success. Helpers are identified by hashes; environment-specific source code is not published.

The actual full run contains 123 task attempts: 122 completed and one historical failed attempt, which is retained and fully superseded by verified successors. Canaries are included in their owning plans and are not counted twice. The prior 10-message recovery is outside these task-attempt totals.

The final audit verified 3,476 auxiliary artifact files through API/local raw SHA256 matches, all 786 affected native tool contexts, all 195 successor source IDs, 42 active corrective/supplement canonical targets, five quarantined partial artifacts, and unchanged shared-case content. The main import audit separately verified 919 distinct current targets at its own checkpoint. These target counts cover different checkpoints and must not be added as unique net growth.

## Failure history and recovery decisions

1. **Conservative boundary, then sealed supplement.** The 67 messages associated with the current conversation were initially deferred. Exact source bytes, message-ID digest, phase-one marker, prior terminal failure, and zero retained/live overlap subsequently proved an older sealed archive. It was recovered in a separate immutable plan, without replaying ongoing turns.
2. **Auxiliary-artifact omission.** An independent native audit found 786 imported ToolParts across 96 recovery sessions whose original blobs were valid but missing from the recovery sessions' own stores. User-memory rendering omitted ToolPart evidence and was unchanged; agent-visible tool prefixes differed. Native session scoping is not asserted to be an upstream defect: this was a recovery importer omission. A no-write native probe demonstrated exact restoration, then the artifacts were copied through the supported native filesystem path and read back. Only the affected 786 contexts were selected for corrective extraction.
3. **Partial corrective task.** One 195-message corrective task failed on an unterminated triple-quoted generated program in the experience merge optimizer after five intermediate trajectory files were persisted. An output-limit/truncation cause was not proven by a reliable finish reason. The failed task and original corrective plan remain intact.
4. **Reversible, verified successor.** Fresh ownership, version/birth/hash, original-snapshot, source-link and inbound/case-reference checks established that only those five intermediate files belonged to the failed attempt. Native filesystem moves preserved them in that attempt's partial-artifact namespace. Five raw hashes matched on readback, shared-case content retained its original hash, and no inbound links referenced the quarantined artifacts. Only the remaining 195 messages were retried in 50/50/50/45-message chunks. All four native tasks and genuine terminal markers completed; the 591 already successful corrective messages were not repeated.
5. **Main import snapshot pair.** The sole adjacent snapshot mismatch involved two captures 2.853 ms apart with identical before-bodies and identical after-bodies. Both complete after-snapshots and all seven added lines remain in the current target. Overlapping capture of the same combined state is consistent with these records, but exact scheduling/merge timing was not isolated. The bounded check found no observed lost update in this pair; it is not exhaustive semantic review of every historical mutation.
6. **Separate successor Case footer.** A different successor target had 14 native managed Linked Experiences relations. Re-rendering its owning Case template with `links=[]` reproduces the recorded business body exactly, with SHA256 `b7f60f4bcbef2c31a855b871b0a4cc1e3b29af29d5ef3dc3560d8c633b831264`. This explains that target's body/footer difference and is separate from the main snapshot-pair check.

No synthetic completion markers, global backend patch, daemon restart, source-message suppression, or replay of protected ongoing messages was used. The 3,925 semantic-sequence duplicate candidates were retained because they carried distinct original source IDs.

## Result accounting and current retrieval

The main diffs recorded 760 add, 210 update and two delete operations. The corrective/supplement diffs recorded 27 add and 17 update operations; those 27 add operations include five partial trajectories later quarantined. These are historical operation counts, not 27 current new memories or net file growth. Current canonical targets and quarantined files were independently verified in their actual namespaces.

The final audit reports zero audit errors while retaining one historical task failure; these are separate counters. That failure's 195 source IDs are fully covered by the four successful successors. The task error was not erased to make the totals look clean.

After completion, registered MCP find requests retrieved two newly created canonical targets, one global and one project-scoped, with each query bound to its exact target URI. This proves sample indexing/retrieval, not corpus-wide ranking quality. Post-audit HTTP health reported 200, healthy=true, version 0.5.3. Final readiness was not rerun.

## Evidence map

| Evidence | Purpose |
| --- | --- |
| `final-combined-fidelity-audit-summary.json` | Final independent coverage, faithful visibility, artifact hashes and superseded-failure checks |
| `main-import-coverage-summary.json` | Original 104-chunk import and first current-target audit |
| `initial-auxiliary-artifact-fidelity-summary.json` | Preserved initial fidelity failure |
| `fidelity-partial-audit-summary.json` | Preserved 591/786 checkpoint and incomplete state |
| `verified-partial-artifact-quarantine-summary.json` | Reversible five-file move, original hashes and unchanged case |
| `successor-195-progress-summary.json` | Four genuine successor completions and native visibility proofs |
| `main-diff-chain-independent-review-summary.json` | Bounded main snapshot-pair readback and preserved added lines |
| `managed-link-independent-review-summary.json` | Separate successor Case native-template/body-footer reconciliation |
| `semantic-retrieval-summary.json` / `final-health-summary.json` | Post-recovery access checks |
| `provenance-summary.json` | Original input-output hashes/sizes and redaction policy |

## Boundaries and rollback

Coverage certifies processing and faithful archived input/context, not that every message yields a new memory or that every generated fact was manually adjudicated. The separate startup recall-compressor delay was unchanged and not tested by this follow-up. No hardware, RF, or electrical claim is made.

Original archives and the failed attempt remain preserved. The five quarantined intermediates have a reversible move journal and verified original hashes. Recovery records, copied auxiliary artifacts, immutable plans, predecessor/successor lineage, and the full-store backup support investigation and rollback. No bulk rollback was performed or represented as tested. Public evidence omits raw conversations, memory titles/URIs, private identities, credentials, endpoints, machine paths and raw backups; prior partial/failure summaries remain intact.
