# BeaconHound 0.1.0 arm64 package review

## 1. Context

`m5stack/CardputerZeroRepository` is the Debian repository for CardputerZero
applications. Submissions arrive as PRs that add a `.deb` under `incoming/`; CI
validates the package with `dpkg-deb` and the maintainer merges, after which
`publish.yml` uploads the file to the `apt-pool` release and rebuilds the index.

PR #2 adds a single file, `incoming/beaconhound_0.1.0_arm64.deb`, from a
first-time contributor. The PR body is one line: "Initial Community release of
BeaconHound." The repository is at `ci/bootstrap` (default branch), not `main`.

## 2. Method

Everything below was done on the exact PR blob, not on a downloaded release:

```bash
git clone https://github.com/m5stack/CardputerZeroRepository
git fetch origin refs/pull/2/head:pr2
git cat-file -p pr2:incoming/beaconhound_0.1.0_arm64.deb > beaconhound.deb
git hash-object beaconhound.deb   # fcad30d2b8c458079f9ec4ded9bb06a976147b99
shasum -a 256 beaconhound.deb
ar x beaconhound.deb
tar xzf control.tar.gz -C ctl && tar xzf data.tar.gz -C dat
diff <(tar xzOf control.tar.gz ./md5sums | ...) <(md5 of extracted files)
llvm-readelf -h/-l/-d/--dyn-syms both binaries
strings -a -t x, llvm-objdump -d (argv construction and execv calls)
sh -n ctl/postinst ctl/prerm
```

`dpkg-deb` is not installed on this macOS host, so the control file was read
directly from `control.tar.gz`; all fields relevant to the repo's validator
(`Package`, `Version`, `Architecture`, filename) were checked against
`validate-submission.yml`.

## 3. What is correct

- `debian-binary` is `2.0`; ar member order is `debian-binary`, `control.tar.gz`,
  `data.tar.gz`; both gzip streams pass `gzip -t`.
- `DEBIAN/md5sums` covers all 7 payload files and every digest matches the
  extracted bytes.
- `Package: beaconhound`, `Version: 0.1.0`, `Architecture: arm64`; filename is
  `beaconhound_0.1.0_arm64.deb`, which matches the validator's regex.
- Both executables are AArch64 PIE ELF, interpreter
  `/lib/ld-linux-aarch64.so.1`, `NEEDED` only `libc.so.6`, highest symbol
  `GLIBC_2.34`, consistent with `Depends: libc6 (>= 2.34)`. GNU_STACK is RW
  (non-executable), GNU_RELRO is present; no RPATH/RUNPATH.
- `postinst` and `prerm` are syntactically valid POSIX sh (`sh -n`) and only act
  on `configure` / `remove` / `deconfigure`.
- The desktop entry and icon follow the `/usr/share/APPLaunch` layout used by
  other CardputerZero packages (`Icon=share/images/<id>.png` relative form).
- The socket is created with `chmod 0660` (immediate `0x1b0` before the `chmod`
  call), not world-writable.

## 4. Findings

### F1. `User=pi` conflicts with the device account model (blocking)

`usr/lib/systemd/system/beaconhound-lite-daemon.service:7-8` hard-codes
`User=pi`/`Group=pi`. `DEBIAN/postinst:7` gates the whole enable/restart block on
`id -u pi`; if the account is absent the script exits 0 and prints nothing.

The official CardputerZero usage guide says the Linux username is chosen in the
first-boot setup wizard ("follow the setup wizard to set a username", also
`{username}` in later paths):
https://docs.m5stack.com/en/compute/cardputerzero/usage

Consequences:

- Username != `pi`: the package installs and reports success, but the daemon is
  never enabled, so the UI has no telemetry endpoint.
- Username != `pi` but a `pi` account exists: the daemon runs as `pi`, creates
  `/run/beaconhound/engine.sock` with mode 0660 owned by `pi:pi`, and the UI
  running as the desktop user cannot connect (same 0660 restriction on the
  `RuntimeDirectory`-owned socket).

A service template (`User=%i`), a user unit for the desktop account, or
install-time detection of the actual account would all resolve this; the choice
belongs to the repository owner.

### F2. Scan path has no `CAP_NET_ADMIN` (blocking)

The daemon builds `argv = {iw, dev, <iface>, scan, dump}` from `.rodata` at
`0x3a50`-`0x3a68`, then calls `execv("/usr/sbin/iw")`, `execv("/sbin/iw")`, and
`execvp("iw")` in that order; it parses `freq:` from the child's stdout. The
`iw ... scan` path is an nl80211 `TRIGGER_SCAN`, which the kernel allows only
with `CAP_NET_ADMIN`.

The unit runs as an unprivileged user with `NoNewPrivileges=true` and no
`AmbientCapabilities=` or `CapabilityBoundingSet=`. Under that unit the child
`iw` is expected to fail with `EPERM`, so the HUD cannot receive scan results.
`AmbientCapabilities=CAP_NET_ADMIN` plus a matching `CapabilityBoundingSet` (with
`NoNewPrivileges` retained) is the minimal change; running the whole daemon as
root is not required.

This is a static inference from the unit and the call path, not a measured
runtime failure; see the limits in section 6.

### F3. CI has not validated the package (process blocker)

The `validate-submission` run for this PR is `action_required` with 0 s and no
jobs (run 44433521771): GitHub is holding the fork PR's workflow for maintainer
approval, so it has not executed. `docs/MAINTAINERS.md` requires a green run and the
`dpkg-deb -I` log before merge; neither exists. The author cannot clear this
alone.

## 5. Non-blocking observations

- `Recommends: beaconhound-pro` names a package that is not in this repository;
  apt ignores an unavailable Recommends, so this is cosmetic.
- The control `Description` line 12 starts with one space while the paragraph
  above uses two; it renders as a line break rather than a paragraph break. Not
  a validity problem.
- The package auto-enables and restarts a background daemon on install. That is
  a policy decision for the repository, not a packaging defect.
- The `Homepage` repository (`pingequalab/beaconhound`) exists but is empty at
  review time (created 2026-11-19T00:55Z, size 0, no releases or sources), so
  the binaries cannot be compared with a public build.

## 6. Limits

- Evidence class is **code-level verification**: archive/control/ELF/static call
  path only. The package was not installed and neither binary was executed.
- No CardputerZero hardware was attached; the hardware test center exposes only
  ESP32 slots.
- The Device Service has a `cardputer-zero` profile (RP3A0, `linux-arm64`) but it
  is `supported=false`, `creatable=false`, with
  `missing_runtime_files: ["__missing_qemu__", "__missing_rom__"]` and reason
  "CardputerZero uses a separate Linux backend", so it cannot boot this image.
- An arm64 Debian container was considered for a host-level install test, but the
  local Docker daemon could not write its metadata store on this host (read-only
  filesystem), and the host had ~4 GiB free, so no image was pulled.
- F2 is an expected-failure inference, not an observed EPERM; a device run with
  `journalctl -u beaconhound-lite-daemon` would settle it.

## 7. Disposition

One review comment was posted on the PR with F1, F2 and F3 and the evidence
class: https://github.com/m5stack/CardputerZeroRepository/pull/2#issuecomment-6996544162
(2026-11-19T01:10:21Z). No code was pushed to the PR or the fork and the PR was
not closed.
