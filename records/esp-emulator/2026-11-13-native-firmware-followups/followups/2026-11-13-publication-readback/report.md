# Publication verification

The nine issue replies were posted only after their virtual-device evidence had been archived and published. Comment bodies and resulting states were read back and matched; four issues were closed and five remained open. The readback summary retains the exact public reply URL and body SHA-256 for each.

The subsequent source documentation commit was checked against its exact GitHub Actions head SHA and terminal success status. A Git comparison confirms all changes are documentation. This follow-up does not redeploy services, replace runtime evidence, erase prior failures, or extend the functional acceptance scope.

# Main documentation and issue publication readback

The preceding [validated runtime record](https://github.com/m5agent/agent-work-logs/blob/f611cf14e32459668de9cef5ac5e9e951c862977/records/esp-emulator/2026-11-13-native-firmware-followups/followups/2026-11-13-main-and-resident/README.md) was published at public commit `f611cf14e32459668de9cef5ac5e9e951c862977`. Its historical `PRIVATE_RENDERED_NOT_PUBLISHED` render field describes the state when generated; this append records actual subsequent publication.

The documentation-only source commit `f855a744277e6644d8d0bf2917a149eb95cc1a68` passed [CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43420460376). All 18 changed files are under `docs/`; executable source and deployed runtimes remain those of `4f09fcba8364e02cb1f60eeec0422e3cae66db54`.

| Issue | Verified state | Reply |
| --- | --- | --- |
| #192 | CLOSED | [Published reply](https://github.com/m5agent/m5stack-esp-emulator/issues/192#issuecomment-6851967836) |
| #205 | CLOSED | [Published reply](https://github.com/m5agent/m5stack-esp-emulator/issues/205#issuecomment-6851969956) |
| #221 | CLOSED | [Published reply](https://github.com/m5agent/m5stack-esp-emulator/issues/221#issuecomment-6851971888) |
| #222 | CLOSED | [Published reply](https://github.com/m5agent/m5stack-esp-emulator/issues/222#issuecomment-6851973948) |
| #216 | OPEN | [Published reply](https://github.com/m5agent/m5stack-esp-emulator/issues/216#issuecomment-6851975942) |
| #223 | OPEN | [Published reply](https://github.com/m5agent/m5stack-esp-emulator/issues/223#issuecomment-6851977265) |
| #225 | OPEN | [Published reply](https://github.com/m5agent/m5stack-esp-emulator/issues/225#issuecomment-6851978559) |
| #226 | OPEN | [Published reply](https://github.com/m5agent/m5stack-esp-emulator/issues/226#issuecomment-6851980307) |
| #188 | OPEN | [Published reply](https://github.com/m5agent/m5stack-esp-emulator/issues/188#issuecomment-6851981687) |

These are the observed publication states, not a claim that every firmware or controller gap is resolved. Five issues remain open with the boundaries in their replies. No additional guest execution or physical measurements were performed for this publication-only follow-up; functional evidence remains bound to the prior firmware and runtime identities. Burner was not submitted.

See [structured readback](evidence/publication-readback-summary.json) and [execution record](run.json).
