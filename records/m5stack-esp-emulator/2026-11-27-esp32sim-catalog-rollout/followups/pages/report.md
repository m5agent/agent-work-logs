# Pages evidence for the esp32sim catalog rollout

Emulator main `16faae71c3ee67f5158431dbe78c27e726e67d3d` and esp32sim `4e257b6be8ee0ed706c2e509d8f31ef7472a424b` were tested in separate native and browser lanes. The same merge tree is used for both distributions. Physical hardware was NOT RUN because this work qualified the virtual execution paths.

## Hosted QEMU-WASM gate

[Hosted attempt one](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/45973383714/attempts/1) failed in the Cardputer-ADV IRQ keyboard case after trusted `APOSTROPHE` pointer edges reached the board model. It captured neither the expected controller pair nor guest IRQ press/release for that sample. The failure report includes a subsequent pointer-wait timeout and a failed normal shutdown assertion. [An earlier hosted run](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/45942728417) had already failed the same keyboard case, at a different input. [PaperDIY reset](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/45930498931) and [Atom Matrix editor](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/45941756439) and [model button](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/45939599561) failures were separate observations. The hosted esp32sim export, its guest checks and the unmodified CoreMatrix stock case passed before the separate QEMU-WASM aggregate stopped after seven of 72 cases. The retry was canceled after locating the prior keyboard failure and finishing the full local gate.

## Exact prepared export

Local browser virtual-device validation passed all 72 independent cases in hardware ANGLE, two guests at a time, with per-case input/output and cleanup checks. The cases comprise 23 UIFlow editors, 23 model button suites, the full ADV keyboard suite, StackChan body touch, and 24 fixed examples. The ADV workbench composed image SHA-256 is `b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd`. Xtensa QEMU WASM SHA-256 is `8067a6b8d599f81bfe454da0318377fcb783c8ee4198fc69d3a042c1311d2c1e` in both lanes. The prepared export's C61 WASM has its own hash and CoreMatrix gate receipt. Hosted and local manifests and verdicts remain separately identified in [the receipt](run.json).

The published bundle contains 2,206 manifest assets. The original tarball and release download independently matched SHA-256 `c469933facba74815b1cd0bd043503ecdb7a5740a4c4e9d4021e71bd8138568a` and all manifest asset bytes. This includes only the documented Espressif mask ROM ELF from release `20260528`, 949,552 bytes and SHA-256 `c0ce0f338d1de1bdc6efbef1591779a2a42c1ab7d759d3c6ae8ae63a7dd34cfd`. The runtime manifest, NOTICE and ROM license identify the same Apache-2.0 release. The bundle contains no guest firmware.

## Public readback

The published release is [pages-20261127-16faae71](https://github.com/m5agent/m5stack-esp-emulator/releases/tag/pages-20261127-16faae71) and the [prepared workflow](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/45977378089) deploys its verified release tarball. The previous public manifest SHA-256 was `f55e7c996e0ca2707c72d2b9b7478e6961563a198b61f031e1913d8a19cac914`. The expected new SHA-256 is `d4173a67ed2a0bb72511e5b37cc3cb9fb01a26641c73f3013d5702085c3cd3b3`.

The prepare and deploy jobs passed. The public HTTPS manifest matched the release byte for byte. The live browser loaded the pinned esp32sim WASM and passed the Cardputer keyboard and factory UIFlow2 cases in a cross-origin iframe. The matrix key and GPIO0 press/release reached the model, both firmware runs redrew the 240 × 135 guest framebuffer in response to input, and both runs stopped with zero Dedicated Worker targets. Image, Flash and framebuffer hashes are in the [live-browser receipt](run.json).

The independent HTTPS asset audit downloaded all 2,206 manifest assets and matched every declared size and SHA-256, including the runtime, ROM ELF and corresponding source archives.
