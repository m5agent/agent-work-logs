# OpenViking session extraction recovery report

> Follow-up: [complete historical backlog and fidelity audit — PASS](followups/2026-11-06-historical-backlog/executions/2026-11-06-batch-01/report.md). This later execution supersedes the original all-history NOT RUN boundary while retaining this scoped report and its evidence. The separate startup recall compressor was unchanged.

## Background and target behavior

The target behavior is a session commit that completes long-term extraction, with a safe way to recover one previously failed archive without duplicating messages or commits. Readback of the exact write targets was validated independently from task completion. This public record documents reusable OpenViking `v0.5.3` adapter, protocol, and recovery behavior. It excludes private conversations, machine paths, connection values, credentials, operational backups, and account identities.

## Result and scope

The selected extraction and recovery path passed. Overall status is `PARTIAL` because bulk historical recovery and independent recall-startup performance remain outside the validated scope. The active conversation was excluded from the recovery operation; no conclusion about its future automatic capture is drawn.

The isolated ten-message recovery reported one write operation and two edit operations. The live recovery of the same source archive reported three write operations and two edit operations, with terminal task and phase states both `completed`. These per-run counts differ; model sampling and existing state were not independently controlled, so the cause of that difference is not isolated. A write-operation counter alone does not prove a new file; subsequent canonical readback independently confirmed three added project-peer files and two updated global user-memory files.

A repeated live recovery preserved ten messages, one commit, and the same completed extraction result. The source archive SHA256 was `f896ffb3f8a0edaf459765bb638d10f5dec059f4d3ec2312d5e87d2e2e41cb2d`.

## Failure classification and applied change

The extraction failure path involved an incompatible thinking/tool-choice request combination. The correction pins the published `openviking[bot]==0.5.3` package, selects its `openai-codex` Responses adapter, and sets `reasoning_effort = none`. Existing provider connection settings, embedding configuration, and unrelated server settings were preserved. No custom upstream patch was required.

The pinned release's extraction output protocol accepts an omitted or empty optional `supersedes` field while retaining required-field validation. This behavior was checked directly rather than weakening required schema fields. Working memory remains disabled by the standard default, and the scoped recovery commit explicitly disables it. No root-level memory-policy override or legacy thinking flag was added to the Responses request.

An initial package installation omitted the pre-existing `bot` optional dependency extra, and that startup attempt failed. Installing the exact final requirement with the extra restored the required integration and allowed the final server and integration startup to succeed. The final zero-error interval excludes that earlier failure; it is not a claim that the deployment had no failed attempts.

## Reusable recovery algorithm

1. Choose one failed archived transcript; exclude the current active conversation. Record its byte length, SHA256, ordered messages, and explicit message limit.
2. Derive a deterministic recovery identity from the source and recovery plan. Keep an atomic local ledger and an exclusive execution lock. Keep private identities outside the public record.
3. Preserve the source archive. Create a separate recovery session and append only verified missing messages in order. Refuse continuation if the source digest or existing recovered messages disagree with the recorded plan.
4. Before committing, inspect the recovery session's existing commit and archive state. Do not issue a second commit for a previously committed plan. Do not automatically retry state-changing POST requests after ambiguous failures.
5. Commit once with working memory explicitly disabled. Observe the asynchronous task and long-term extraction completion markers; a successful HTTP command alone is insufficient.
6. Verify the recovered message count, commit count, completed phase/task state, extraction results, and supported retrieval path.
7. Run the same recovery plan again and confirm that messages and commits remain unchanged. Retain the failed source and recovery ledger for follow-up instead of overwriting the original failure evidence.

The private helper implementing this plan is not published because it includes environment-specific plumbing. The algorithm and source/result digests are sufficient to describe the validated safety properties; this record does not present an untested generic replay utility.

## Executable evidence

### Protocol and policy

Pinned upstream regression cases exercised three optional-supersedes variants, two required-field controls, and four working-memory-policy variants. All nine passed. This preparatory probe did not write production state.

### Actual model adapter

The candidate `CodexVLM` adapter made two real Responses requests. The first returned one `record_probe_marker` function call with validated arguments. After the tool result, the second response matched the expected acknowledgement. Both requests used streaming and `reasoning.effort = none`, and omitted `tool_choice` and legacy thinking flags. The measured two-request round trip was 2.026 seconds; this single functional check is not a performance benchmark.

### Session recovery, readiness, and retrieval

The selected ten-message recovery completed in an isolated environment before the live recovery. The live run reported five memory operations (three writes, two edits); repeating it left the recovered messages and commit count unchanged. The isolated service was stopped after its checks.

The final service reported version `0.5.3`, successful health and readiness responses, and healthy storage, vector database, authentication manager, and embedding checks. Authenticated MCP discovery listed 24 tools. Registered MCP health and semantic find tools then executed successfully; the find operation requested at most two items and returned two. Private query/result text is omitted. This semantic find checked previously known memories. A separate canonical-content readback verified all five recovered targets: API content matched local bytes and SHA256 values, and each recorded post-change value was present in the current content. The three added files were in project-peer scope; the two updates were in global user-memory scope. The VLM doctor check is configuration-only evidence; the actual model and extraction checks above separately exercise the runtime path.

### Integrity and log boundaries

Before extraction recovery writes, all 7,582 original Markdown files in the global user-memory subtree were present and byte-identical after the package/configuration migration. This comparison covers that global subtree, not the entire peer-scoped store. It does not assert that extraction leaves intentionally edited memory files unchanged. The three subsequently added peer-scoped files lie outside this counted subtree; a preserved full-store snapshot supports rollback.

The final successful-startup-to-validation log interval contained zero error-level lines. Its byte count and SHA256 are archived without raw log content. This interval does not include the initial missing-extra startup failure.

| Validation layer | Status | Evidence or boundary |
| --- | --- | --- |
| Protocol regression | PASS | Nine bounded protocol/policy variants |
| Model tool-call/result transport | PASS | Two real Responses requests with validated markers |
| Scoped full session extraction | PASS | Ten recovered messages; task/phase completed; five live memory operations |
| Repeated recovery | PASS | Same ten messages, one commit, and completed result |
| Exact canonical target readback | PASS | Three added peer-scoped files, two updated global files; all five API/local hashes and post-change values match |
| Original data after migration | PASS | Global user-memory subtree: 7,582 original Markdown files; zero missing or changed, before recovery writes |
| Readiness and registered MCP execution | PASS | Authenticated 24-tool discovery plus actual health/find calls |
| Bulk historical recovery | NOT RUN | One selected failed archive only |
| Recall startup latency | NOT RUN | Separate compressor path intentionally unchanged |
| Hardware / virtual device | NOT RUN | This record validates the service's actual software path |

## Limits and rollback

These results establish readback of the five recovered targets. They do not establish complete recovery of every historical failure, identical extraction outputs for every provider, or changed recall startup latency. The session-count checks establish scoped repeatability of the recovery operation, not global deduplication of all historical memories.

Rollback requires stopping writes, restoring the saved prior environment and configuration together with the pre-change data snapshot when data rollback is intended, and verifying service and session consistency before resuming. A package downgrade by itself is not represented as a validated data rollback. The original failed archive is retained; the running conversation was not replayed.

## Provenance and redaction

OpenViking source behavior is pinned to [release `v0.5.3`](https://github.com/volcengine/OpenViking/tree/v0.5.3). Evidence files are derived summaries, with input-output hashes and sizes recorded in `provenance-summary.json`. Session labels are aliases. No raw conversation, credential, endpoint, private filesystem path, source configuration, or backup is included.
