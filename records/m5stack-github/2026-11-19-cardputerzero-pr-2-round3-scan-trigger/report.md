# Third-round review: beaconhound 0.1.0 arm64 (CardputerZeroRepository PR 2)

## Context

`m5stack/CardputerZeroRepository` PR 2 adds `incoming/beaconhound_0.1.0_arm64.deb`, a
keyboard-driven wireless HUD for CardputerZero. Round 1 of this review found a hard-coded
`User=pi` and a scan path that only read the cfg80211 cache. Round 2 confirmed the
templated unit but showed that `iw dev <iface> scan dump` needs no capability and never
starts a scan, and that `SUDO_USER` was preferred over the active seat0 user.

The author replied (`#issuecomment-7001204495`) with a rebuilt package, 501,370 bytes,
SHA-256 `19a39a46…2cd7d`, claiming a self-contained two-phase trigger-based scan loop and
a reordered seat0-first account detection.

## Question

Are the two requested changes present and coherent in the new artifact, is the retained
`CAP_NET_ADMIN` now justified, and does anything else in the delta block merge?

## Method

1. Download the exact PR head blob (`68c7dbb8`) through the contents API and compare size
   and SHA-256 with the author's comment.
2. Unpack with `ar`/`tar`, re-verify `DEBIAN/md5sums` against the extracted payload,
   re-check control metadata, `sh -n` on all maintainer scripts, and ELF headers.
3. Diff the payload and control members against the round-2 artifact (`67195a6`) to bound
   the change surface.
4. Disassemble `beaconhound-lite-daemon` (`llvm-objdump`, AArch64) and reconstruct the
   scan state machine: argv construction, exec paths, process-group handling, poll
   deadlines, scheduling constants, exit-code classification, and `freq:` parsing.
5. Cross-check the CLI contract against Debian iw 6.9 (`scan.c`, `iw.c`) — the version
   shipped by trixie, which the package targets (systemd ≥ 256 handling in postinst).
6. Re-read `postinst` for the detection order and the seat0 row/class filters.
7. Query the local Device Service for the `cardputer-zero` profile and attempt an arm64
   Linux container to see whether any runtime path is available.

## Findings

### 1. Artifact identity — match

501,370 bytes and SHA-256 `19a39a46…2cd7d`, identical to the comment. All 7 `md5sums`
entries verify. Control unchanged (`Package: beaconhound`, `Version: 0.1.0`,
`Architecture: arm64`, `Depends: iw, wireless-regdb, libc6 (>= 2.34)`). Both executables
remain AArch64 PIE with `NEEDED libc.so.6` only.

### 2. Scan path — corrected and self-contained

- Child argv is built from the rodata table at `0x48e1`–`0x490b`:
  `{"iw","dev",<iface>,"scan","trigger",NULL}` for the trigger call and
  `{"iw","dev",<iface>,"scan","dump",NULL}` for the harvest call.
- Execution is `execv("/usr/sbin/iw", …)` then `execv("/sbin/iw", …)`, `_exit(127)` if
  both fail. `execvp` is no longer imported — the claim of removing PATH lookup holds.
- The child calls `setpgid(0,0)`; the parent also calls `setpgid(pid,pid)`. On timeout the
  parent sends `SIGKILL` to `-pid` and to `pid`, then reaps with `waitpid` (two call
  sites), so the watchdog cannot leave an orphan holding the pipe.
- Trigger window is 250 ms; the dump window is 300 ms (unchanged from the previous
  round's dump helper).
- On a successful trigger (`0x3c00`) the state stores `next_trigger = now + 10000` and
  `next_dump = now + 1500` from the constant quad at `.rodata 0x48d0/0x48d8`; after a
  dump the schedule advances by 3000 ms (`0x423c`), matching the described 3,000 ms
  steady-state cadence.
- EBUSY is detected by exit status 240 (`-16`) or the literal `(-16)` in stderr
  (`0x3a64`/`0x3a6c`), then retries the trigger at `now + 2000` and clamps the next dump
  to `<= now + 1000`.
- EPERM/EACCES is detected by exit status 255/243 or the literals `(-1)`/`(-13)`, with
  1/2/127 excluded from that branch, and latches into dump-only mode.
- Other failures retry every 10,000 ms with a 60 s (59,999 ms) log throttle.
- The line parser strips leading spaces/tabs, then anchors `strncmp(line,"freq:",5)`,
  `strtol`s the value and counts only 2412–2484 MHz; the line buffer is 512 bytes and is
  reset at each newline, so long IE lines cannot swallow later entries.
- `BH_ENABLE_TEST_HOOKS` and mock hooks are absent from the stripped production ELF.

Why the capability is now correct: `scan trigger` is `NL80211_CMD_TRIGGER_SCAN`, which is
declared with `GENL_UNS_ADMIN_PERM`, while `scan dump` (`NL80211_CMD_GET_SCAN`) is not.
Debian trixie's iw 6.9 has `COMMAND(scan, trigger, …)` → `NL80211_CMD_TRIGGER_SCAN`, so
the invoked syntax exists on the target distribution, and the ambient capability is what
lets the unprivileged daemon's `iw` child pass the netlink permission check.

Minor correction to the author's description: iw's usage path exits 3, not 2 (`iw.c`
`exit(3)`), and `main` returns `-errno`, which produces 255/243/240. The classifier is
still safe because the usage text contains neither `(-1)` nor `(-13)` and falls through to
the generic 10 s retry path.

### 3. Account handling — seat0 now first

`bh_detect_target_user` order is: (1) an existing valid enabled template instance,
(2) active/online local seat0 sessions with `Class` in `user*`, (3) `PKEXEC_UID` /
`SUDO_USER`, (4) running `user@<uid>.service`, (5) first interactive local user with a
home directory. The seat0 block (postinst 110–188) now precedes the sudo/pkexec block
(190–201), which resolves the round-2 edge where an admin's `sudo` identity could capture
the `0600` socket.

The row heuristic assumes the 9-column `loginctl list-sessions` layout of systemd ≥ 256
(leader/class). On an older layout the hint degrades to the fallback value and
`loginctl show-session -p State -p Class` still decides, so the failure mode is a
fallback rather than a wrong pick. `prerm`/`postrm` still stop and disable all template
instances plus the legacy unit and reload systemd.

### 4. Change surface — narrow

Payload diff against `67195a6`: only `usr/bin/beaconhound-lite-daemon` and the unit
`Description` changed; `usr/bin/beaconhound-ui` is byte-identical. Control members
`control`, `prerm`, `postrm`, `md5sums` are unchanged; `postinst` changed only by the
seat0 block and `"${1:-}"` hardening.

### 5. CI — still not executed

Run 44469413044 for head `68c7dbb8` is `action_required`, 0 s, no jobs. The workflow only
runs `dpkg-deb -I`, `Architecture`, filename and size checks; it does not install the
package or exercise the unit/capability. Approval requires write access to
`m5stack/CardputerZeroRepository`; the reviewing account has read-only access.

## Limits and risks

- **Code-level only.** The package was not installed and neither binary was executed.
  No claim is made about runtime behaviour, actual `iw` success, or radio behaviour.
- **`brcmfmac` behaviour is untested.** The design omits `lowpri`/`passive`/fixed
  frequency lists for FullMAC compatibility, but whether a wildcard trigger returns
  `EBUSY` continuously while NetworkManager or wpa_supplicant holds the interface can only
  be established on hardware; the code degrades to 2 s retries and a dump-only latch.
- **Handover pause unverified.** The `kismet_handover_active` gating is not identifiable
  in the stripped binary without the matching sources, so it is unverified rather than
  confirmed.
- **No shadowing run.** The engine binary's build environment and tests were not rerun;
  the author's container results are taken as reported.

## Recommended next step

One hardware run on a CardputerZero before merge: `systemctl status` for the enabled
template instance, `journalctl -u beaconhound-lite-daemon@<user>` for the 10 s trigger /
3 s dump cadence and absence of EPERM, and a comparison of `iw dev wlan0 scan dump |
grep -c 'freq:'` with the HUD count to prove the harvest sees the same cache.
