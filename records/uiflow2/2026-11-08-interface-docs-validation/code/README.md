# Exact executed probes

These files are exact copies of the five executed source inputs. Each probe runs in a fresh CoreS3 virtual device. The native application remains the pinned preview firmware and only the VFS carries code and fixture inputs.

| Source | Done marker | Notes |
| --- | --- | --- |
| [display.py](display.py) | `DOC_TOP3_DONE DISPLAY` | 29 methods,99 required omissions,58 accepted calls and requires [fixtures](fixtures/doc-fixture.png) plus the JPEG/BMP fixtures in the same directory |
| [adc.py](adc.py) | `DOC_TOP3_DONE ADC` | hardware/machine identities and independent methods on public Pin6 ADC1 |
| [m5ui-auto.py](m5ui-auto.py) | `DOC_TOP3_DONE M5UI` | Deliberately no explicit caller M5.begin and finite frame flush |
| [m5ui-explicit.py](m5ui-explicit.py) | `DOC_TOP3_DONE M5UI` | Explicit begin and rotation1 before init and independent guest |
| [m5ui-example.py](m5ui-example.py) | `DOC_TOP3_DONE M5UI_EXAMPLE` | [Exact candidate](m5ui-example-candidate.py) prefix, followed only by observation code |

The generated fixtures are [PNG](fixtures/doc-fixture.png), [JPEG](fixtures/doc-fixture.jpg), [BMP](fixtures/doc-fixture.bmp), each a bounded8x8 generated test input. Source/fixture SHA256 and exact byte sizes are in [session receipts](../evidence/session-receipts-summary.json). Image argument acceptance is tested and codec-wide rendering validation remains outside this record.

Use the existing Device Service session client and command pattern in [report.md](../report.md). Keep session history. Capture frames and API/ZIP/serial provenance before stopping the owned guest. Do not execute through a direct QEMU runner.
