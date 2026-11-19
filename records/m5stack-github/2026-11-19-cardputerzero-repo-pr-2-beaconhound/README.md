# m5stack/CardputerZeroRepository #2: beaconhound 0.1.0 (arm64) package submission

- Date: `2026-11-19`
- Result: `REVIEW` (artifact and code-level inspection only; the package was not installed or executed)
- Work type: `pr_review`
- Source: https://github.com/m5stack/CardputerZeroRepository/pull/2 (opened 2026-11-19T01:00:23Z by pingequalab, open, no prior comments)
- Source version: PR head `147196989af3a4ef31f7d3764f803a571be3b714` on base `ci/bootstrap` (`c817f795c5a1597e13b428296130bd043df71a23`), one added file, 497,010 bytes
- Comment: https://github.com/m5stack/CardputerZeroRepository/pull/2#issuecomment-6996544162 (2026-11-19T01:10:21Z)
- Artifact: `incoming/beaconhound_0.1.0_arm64.deb`, git blob `fcad30d2b8c458079f9ec4ded9bb06a976147b99`, SHA256 `46f6d41a5f3a0dbe4bc02843917e5ee3929dd327c5be3f32d181fbf224d2ec10`
- Environment: macOS arm64; no CardputerZero hardware; local Device Service `cardputer-zero` profile is not creatable
- Evidence class: **code-level verification** (package structure, control metadata, ELF headers/dynamic deps, maintainer scripts, static call path)

## Conclusion

The archive itself is well formed and correctly declared for arm64, but the packaging
model conflicts with how CardputerZero accounts are created. Two changes are needed
before merge:

1. **The service hard-codes `User=pi`.** The official first-boot wizard lets the user
   choose the Linux username, and `DEBIAN/postinst` only enables the unit when a `pi`
   account exists (`id -u pi`). Any other username installs "successfully" with the
   daemon never enabled and no error shown. Even when `pi` exists, the daemon socket is
   `chmod 0660` owned by `pi`, so a UI running as the desktop user cannot connect.
2. **The scan path has no capability grant.** The daemon runs
   `iw dev <iface> scan dump`, which needs `CAP_NET_ADMIN`; the unit runs as `pi` with
   `NoNewPrivileges=true` and no `AmbientCapabilities`/`CapabilityBoundingSet`.

CI has not validated the submission: the `validate-submission` run for this PR is
`action_required` (0 s, no jobs), so no `dpkg-deb -I` log exists yet, while
`docs/MAINTAINERS.md` requires green validation before merge.

## Key evidence

- `evidence/deb-metadata.txt`: ar members, `debian-binary` 2.0, control fields, data
  payload, and a full match of `DEBIAN/md5sums` against the extracted files.
- `evidence/elf-dynamic.txt`: both executables are AArch64 PIE, interpreter
  `/lib/ld-linux-aarch64.so.1`, `NEEDED` only `libc.so.6`, highest symbol `GLIBC_2.34`
  (matches `libc6 (>= 2.34)`).
- `evidence/service-and-scripts.txt`: unit, `postinst`, `prerm`, desktop entry, and
  `sh -n` syntax checks.
- `evidence/daemon-iw-invocation.txt`: `iw`/`dev`/`scan`/`dump` strings, the argv
  build and `execv` fallbacks, and `chmod 0x1b0` (0660) on the socket.
- `evidence/ci-status.txt`: `action_required` validate run 44433521771.
- `evidence/cardputerzero-profile.txt`: Device Service profile (not creatable) and the
  hardware bench inventory (ESP32 nodes only).

## Files

- `report.md`: full review, method, findings, limits
- `run.json`: structured record
- `evidence/`: raw inspection output used above

## Not covered

- `NOT RUN` hardware validation: no CardputerZero on the bench.
- `NOT RUN` virtual-device validation: the Device Service `cardputer-zero` profile is
  `supported=false`, `creatable=false` (`missing_runtime_files: __missing_qemu__,
  __missing_rom__`, reason "CardputerZero uses a separate Linux backend"), and an
  arm64 Debian package is outside the ESP emulator's scope.
- `NOT RUN` install/execute: no arm64 Linux userland was available for a host test.
- Review comments only; nothing was pushed to the PR or the fork.
