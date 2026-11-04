# Guest demonstration sources

These programs are demonstration applications, not changes to the emulator. Use
the matching UIFlow2 virtual-device firmware and the same-session Device Service
submission/input path described in the [report](../report.md).

| File | Device / purpose | Origin |
| --- | --- | --- |
| [arcade-main.py](arcade-main.py) | Cardputer ADV keyboard-controlled brick game; `a`/`d` move the paddle | New demonstration authored for this task by m5agent |
| [paint-main.py](paint-main.py) | CoreS3 palette selection, touch drawing and clear control | New demonstration authored for this task by m5agent |
| [pelican-main.py](pelican-main.py) | CoreS3 bicycle animation with touch and BMI270 input | Unmodified pinned repository source, linked below |
| [workbench-live.py](workbench-live.py) | CoreS3 live-code editor execution and visible ready screen | New demonstration authored for this task by m5agent |

Pelican source: [m5agent/m5stack-esp-emulator at
b41eba70eb61f7ddc5c41e0b981341064f9d1d1f](https://github.com/m5agent/m5stack-esp-emulator/blob/b41eba70eb61f7ddc5c41e0b981341064f9d1d1f/tests/uiflow2/cores3_pelican_bike/main.py).
Copyright (c) 2026 m5agent contributors. The MIT copyright and permission notice is
included unchanged in [LICENSE-MIT.txt](LICENSE-MIT.txt). New demonstration code
is also supplied under that license.

Exact source byte counts and SHA256 values are recorded in the
[source identity summary](../evidence/code-summary.json). The Pelican source was
copied without modification. Its optional speaker path is present in source but
is not granted an audio or physical-acoustics PASS by this video task.

The applications contain generated visuals and simulated inputs. Runtime claims
must use their separately captured firmware/runtime/input evidence; source
inspection or successful import alone is insufficient.
