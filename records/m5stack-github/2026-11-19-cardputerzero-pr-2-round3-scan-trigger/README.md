# CardputerZero PR 2 — third-round re-check of beaconhound 0.1.0 (self-contained scan trigger + seat0 priority)

- Date: `2026-11-19`
- Result: `REVIEW` — code-level; both requested fixes hold, no new blocking finding, package not installed or executed
- Work type: `pr_review`
- Source: https://github.com/m5stack/CardputerZeroRepository/pull/2
- Source version: PR head `68c7dbb8b578d1d649e97c7927a0a66e6db97cc2` (commit 3 of 3), base `ci/bootstrap`
- Artifact: `incoming/beaconhound_0.1.0_arm64.deb`, 501,370 bytes, SHA-256 `19a39a46c71d7a6e2d0cd3f539001de3fc270eee4bf7b837a1c644e522f2cd7d`
- Previous review: comment `#issuecomment-6997380419` on head `67195a6`
- Environment: macOS arm64; no CardputerZero hardware; local Device Service `cardputer-zero` profile is not creatable; arm64 Linux container runtime unavailable (Docker metadata store read-only)
- Evidence class: **code-level verification** (package payload diff, systemd unit, maintainer scripts, AArch64 disassembly, iw 6.9 source cross-check)

## Conclusion

The author's third-round build addresses both items from the previous review:

1. **Self-contained scan is real, and `CAP_NET_ADMIN` is now the correct privilege.**
   The child is executed as `/usr/sbin/iw dev <iface> scan trigger` (fallback `/sbin/iw`),
   not `scan dump`; `scan trigger` maps to `NL80211_CMD_TRIGGER_SCAN`, which carries
   `GENL_UNS_ADMIN_PERM`, so the retained `AmbientCapabilities`/`CapabilityBoundingSet`
   is required rather than unnecessary. `scan dump` is still used, but only to harvest
   the cache `+1,500 ms` after a trigger.
2. **seat0 detection now precedes `PKEXEC_UID`/`SUDO_USER`.**
   `bh_detect_target_user` checks an existing enabled instance, then active seat0
   sessions, then pkexec/sudo, then `user@<uid>.service`, then the passwd fallback, so a
   cross-account `sudo apt install` binds the `0600` IPC socket to the seat0 desktop user.

No new blocking issue was found in the delta. The payload diff against `67195a6` touches
only `usr/bin/beaconhound-lite-daemon`, the unit `Description`, and the postinst seat0
block; `usr/bin/beaconhound-ui` is byte-identical.

Remaining gates are external, not code: the `validate-submission` run is still
`action_required` (maintainer approval required, no `dpkg-deb` log yet), and there is no
install/service-start/`iw` execution evidence on a real CardputerZero.

## Key evidence

- `evidence/deb-metadata.txt`: size/SHA-256 match the author's comment, all 7 `md5sums`
  pass, `debian-binary` 2.0, AArch64 PIE, `NEEDED libc.so.6` only.
- `evidence/payload-diff-vs-67195a6.txt`: only the daemon, unit `Description`, and
  postinst seat0 block changed; UI binary unchanged.
- `evidence/daemon-iw-fsm.txt`: `iw dev <iface> scan trigger|dump` argv table, `execv`
  only (no `execvp`), `setpgid` + `kill(-pid,SIGKILL)` + `waitpid`, 250 ms trigger
  watchdog / 300 ms dump window, 10,000/1,500/3,000/2,000 ms schedule, EBUSY and
  EPERM/EACCES classification, `freq:` anchoring and 2412–2484 filter, no test hooks in
  the stripped ELF.
- `evidence/unit-and-postinst.txt`: unit file, postinst detection order, prerm/postrm.
- `evidence/iw-trigger-and-exit-codes.txt`: Debian iw 6.9 has `COMMAND(scan, trigger)`
  → `NL80211_CMD_TRIGGER_SCAN`; iw returns `-errno` from `main`, so EPERM is 255/EACCES
  243/EBUSY 240, and usage exits 3 (not 2).
- `evidence/ci-status.txt`: run 44469413044 `action_required`, 0 s; workflow only runs
  `dpkg-deb -I`, arch, filename and size checks.
- `evidence/profile-and-runtime.txt`: Device Service profile and the container runtime
  blocker.

## Files

- `report.md`: full review and limits
- `run.json`: structured record
- `evidence/`: raw inspection output

## Not covered

- `NOT RUN` hardware validation: no CardputerZero on the bench.
- `NOT RUN` virtual-device validation: Device Service registers `cardputer-zero`
  (`linux-arm64`, RP3A0) as `supported=false`, `creatable=false`,
  `missing_runtime_files: __missing_qemu__, __missing_rom__`, backend "separate Linux
  backend"; the profile cannot run a Debian package even if created.
- `NOT RUN` install, service start and live `iw` execution: no arm64 Linux userland on
  this host (Docker container creation fails on a read-only metadata store).
- Unverified at code level: the `kismet_handover_active` pause/resume path could not be
  tied to a specific instruction sequence in the stripped binary.
- Review comment only; nothing was pushed to the PR or the fork, and the PR was not
  closed or merged.
