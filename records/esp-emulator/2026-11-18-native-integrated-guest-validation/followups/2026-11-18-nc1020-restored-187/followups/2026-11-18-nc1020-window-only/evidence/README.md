# NC1020 panel address window replay

Virtual-device validation on November 18, 2026. Two fresh offline Device Service 1.87.0 K132 Cardputer sessions booted the same populated Flash and FAT32 card. The factory application was byte-identical to the original NC1020 BIN. Both sessions received zero device inputs and ended with retained evidence, released Flash, and zero active leases. Only the existing `M5SW_SPI_WINDOW_TRACE=1` diagnostic was enabled. The exact source, QEMU, ROM, original BIN, media, ZIP, and frame hashes are in [the receipt](window-only.summary.json).

| Trial | State restored | Panel content windows | Framebuffer across three captures | First heartbeat at cycle 164524339 |
| --- | --- | --- | --- | --- |
| Window A1 | PASS, exact 99,384 bytes | Rows 0–239 | PASS, 25,112 nonblack pixels, same PNG as the untraced passing run | `draws(+1)` |
| Window A2 | PASS, exact 99,384 bytes | Rows 0–208 | PARTIAL, 22,178 nonblack pixels, same partial PNG throughout | `draws(+0)` |

Both trials completed 407 SD single-block reads and emitted identical address windows for native rows 0 and 1. The partial trace's complete 2,338 address records exactly match the first 2,338 records of the passing trace. Its last content window used CASET `003400ab` and RASET `00f800f8` for row 208. All 120 content pixels in every row through row 208 matched the passing image. Row 208 contained 111 nonblack pixels. All 120 content pixels in rows 209–239 stayed black. A2 emitted no further CASET command. A1's next address window used CASET `003400ab` and RASET `00f900f9` for row 209. Eighty-six sidebar pixels outside the content rectangle also differed between the frames.

The separate untraced control restored state in two of two sessions and completed the draw in one of two. Its partial image stopped after row 0. Window tracing retained the partial-draw failure in one of two sessions and did not reproduce that exact row-0 cutoff. These four observations do not establish whether the trace moved the cutoff.

The panel reached a fully painted row before the next window disappeared. A bounded SPI2 transaction diagnostic needs to distinguish the completion and interrupt for the painted row from the next guest submission. DCS window logs alone do not resolve transport completion or guest wait state. Physical hardware and browser execution were outside this probe.
