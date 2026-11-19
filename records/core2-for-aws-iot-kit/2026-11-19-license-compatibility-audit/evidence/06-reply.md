Thanks for the report. I checked `e1c3750` and the pinned `cryptoauthlib` release. The direction is right, but the dependency surface is wider than the `requirements.txt` line, and that changes what the correct fix is.

**Conclusion**

This is a repository-level license-scope gap, not a license incompatibility in the copyleft sense. The Microchip license is permissive with a field-of-use restriction, so MIT-declared code and Microchip code can coexist under their own terms — and every vendored copy here already keeps the Microchip `LICENSE`, which satisfies the redistribution clause. What is missing is that nothing at the repository root states this.

**Evidence — code-level verification**

- Vendored, not only a pip dependency: 5 of the 7 example projects contain `components/esp-cryptoauthlib/cryptoauthlib/`, `version.txt` = `cryptoauthlib-v3.7.9` (Espressif's port of Microchip's library). All 5 preserve Microchip's `LICENSE` (identical file, sha256 `17f8ada09570f01b9e2c3c995f220fce01ffb61c6b8c0199f6f6ac2f355cd7d2`).
- Linked into firmware: `Blinky-Hello-World/main/CMakeLists.txt:3` and `Blinky-Hello-World/components/core2forAWS/CMakeLists.txt:36` require `esp-cryptoauthlib`; `components/core2forAWS/atecc608/atecc608.c` includes `cryptoauthlib.h`. MIT-declared code therefore statically links Microchip code.
- Prebuilt binaries redistributed in-tree: 55 `sample_bins/*.bin` files (`secure_cert_mfg*.bin`, 11 targets × 5 examples), which also triggers the "must include the above terms" clause.
- Root `LICENSE` is MIT (`Copyright (c) 2020 Amazon Web Services`), with no scope disclaimer and no `NOTICE` for this component — the only `NOTICE.txt` files in the tree belong to the vendored AWS IoT SDK. GitHub's `/license` API consequently reports `spdx_id=MIT` for the whole repository. `Blinky-Hello-World` and `Smart-Spaces` have no local license file, so root MIT is all a reader sees there.
- On `requirements.txt:10` specifically: the repository does not redistribute the package; the user's `pip install` fetches it from PyPI. For the pinned `20250916` sdist, metadata is `License: Other` / `License :: Other/Proprietary License`, and its `LICENSE.txt` says "You may use this software and any derivatives exclusively with Microchip products." That line is a disclosure gap, not a redistribution violation.

So your incompatibility conclusion is partly right: MIT alone cannot grant rights to Microchip code, and a repo-wide MIT with no third-party notice invites exactly the reading you describe. It is not that the two licenses cannot coexist in one repository.

**Suggested minimal fix (not applied — I made no changes to the repo)**

1. Add a root `NOTICE` / `THIRD_PARTY_LICENSES.md` covering the vendored `esp-cryptoauthlib` v3.7.9 including the "exclusively with Microchip products" restriction, the 55 `sample_bins/*.bin`, and pip `cryptoauthlib==20250916`, and point at each example's own LICENSE.
2. Scope root `LICENSE` with one sentence: MIT covers first-party code only, except components carrying their own license.
3. Add a per-example license table to the README. The examples already differ — Apache-2.0 for `Getting-Started` and `Smart-Thermostat`, Espressif MIT (itself field-of-use restricted) for `Alexa_for_IoT-Intro` — so one table removes the ambiguity beyond this single dependency.

**Not covered**

- No firmware build was run. "cryptoauthlib is in the shipped image" is established from CMake requires/includes, not from binary inspection.
- Distribution outside the repository (docs, M5Burner images, prebuilt firmware): there are no release assets here, so whether those channels carry the Microchip terms is not verifiable from source.
- Whether a field-of-use restricted license is acceptable for the project's distribution model, including the ESP32-plus-ATECC608 combination, is a maintainer/legal decision; I am not making that call from source.

Detailed artifact inventory and reproduction commands: https://github.com/m5agent/agent-work-logs/blob/7d10e9a/records/core2-for-aws-iot-kit/2026-11-19-license-compatibility-audit/README.md
