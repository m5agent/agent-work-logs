# OpenViking session extraction recovery

> Latest follow-up (2026-11-06): [historical backlog recovery — PASS](followups/2026-11-06-historical-backlog/executions/2026-11-06-batch-01/). It certifies 49,420 newly recovered messages and complete 85,245-ID historical coverage with faithful auxiliary-artifact handling. The original scoped results below remain unchanged; startup recall-compressor latency is a separate unmodified path.

- Date: `2026-11-06` (`Asia/Shanghai`)
- Overall result: `PARTIAL` — the scoped extraction and recovery path passed; bulk historical recovery and separate recall startup latency were not tested or changed.
- Work type: `service_debug`
- Public source: [volcengine/OpenViking `v0.5.3`](https://github.com/volcengine/OpenViking/tree/v0.5.3)
- Runtime: pinned `openviking[bot]==0.5.3`; `openai-codex` Responses adapter with `reasoning_effort = none`.

## Conclusion

A selected failed ten-message archive was recovered through the actual session commit and memory-extraction path. The isolated check reported one write operation and two edit operations. The live recovery reported three write operations and two edit operations. Exact canonical readback confirmed three new project-peer memory files and two updated global user-memory files. Repeating the same recovery preserved ten messages and one commit. The original 7,582 Markdown files in the global user-memory subtree were unchanged by the package/configuration migration, measured before recovery writes.

## Key evidence

- [Runtime recovery](evidence/runtime-recovery-summary.json), [completion](evidence/replay-completion-summary.json), and [idempotence](evidence/replay-idempotence-summary.json): terminal completed state, extraction counts, unchanged message/commit counts, aliased session, and source SHA256.
- [Real model function-call/result round trip](evidence/codex-vlm-roundtrip-summary.json) and [protocol regression](evidence/extraction-protocol-regression-summary.json).
- [Readiness](evidence/service-readiness-summary.json), [registered MCP execution](evidence/mcp-execution-summary.json), and [final runtime log](evidence/final-runtime-log-summary.json): authenticated discovery of 24 tools, actual health/find success, and zero error-level lines during the final successful run.
- [Canonical memory readback](evidence/canonical-readback-summary.json): all five target contents matched their API reads, local SHA256 values, and recorded post-change values.
- [Baseline integrity](evidence/baseline-data-integrity-summary.json) and [evidence provenance](evidence/provenance-summary.json).

## Files

- [report.md](report.md): failure classification, change, recovery algorithm, evidence, limits, and rollback.
- [run.json](run.json): structured results by validation layer.
- `evidence/`: allowlisted summaries; private conversations and connection settings are omitted.
- `patches/`: not applicable; the pinned upstream release supplies the relevant protocol behavior.
- `code/`: not applicable; the private recovery helper is omitted. The reusable recovery algorithm is documented in the report.

## Not covered

All historical failures were not replayed. The active conversation was excluded from recovery. The separate recall-compression startup delay was untouched. Broad model/provider compatibility, throughput, hardware behavior, and virtual-device behavior were not validated. The zero-error log interval begins at the final successful startup and excludes an earlier dependency-installation failure, described in the report.
