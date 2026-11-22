# st7789v SPI id / Cardputer Zero LCD autoload review

## 1. Context

`m5stack/m5stack-linux-dtoverlays` carries the device-tree overlays and
out-of-tree kernel modules for M5Stack Linux products, including Cardputer Zero
(RP3A0 / BCM2837, 320x170 ST7789v panel).

PR #17 is a one-file, five-line change by khalifa-mnt. It adds `st7789v_lcd` to
the SPI id table of `modules/st7789v-1.0/panel-mipi-dbi-m.c`. The author reports
that on a Cardputer Zero running a non-vendor OS image the LCD stays dark because
`panel_mipi_dbi_m` is never autoloaded; `modprobe panel-mipi-dbi-m` by hand brings
the panel up. The PR body attributes this to the SPI modalias being derived from
the first compatible only, and to the missing id-table entry.

The PR is OPEN with no comments and no reviews. Base is `main`
`a3fd3e83c0247e16e194e7e40f7fc1f5be933dd4`; head is
`40022b4a0f0c2d27347c9b520895475dd46b2c21`; scope is `+5/-0` in one file.

## 2. Mechanism

The LCD node in both overlays is:

```dts
display: st7789v@0 {
    compatible = "cardputerzero,st7789v_lcd", "panel-mipi-dbi-m5stack";
```

For a device-tree SPI device, the kernel builds `spi->modalias` from the
compatible property:

- rpi-6.1.y: `of_register_spi_device()` calls `of_modalias_node()`
  (`drivers/spi/spi.c:2337`). `of_modalias_node()` takes the first compatible
  string and copies everything after the first comma
  (`drivers/of/base.c:1223-1234`).
- rpi-6.6.y: the same step is `of_alias_from_compatible()`
  (`drivers/spi/spi.c:2356`), whose documentation says it strips the manufacturer
  prefix "from the first entry in the compatible list property"
  (`drivers/of/base.c:1031-1050`).

Both yield `st7789v_lcd` for `cardputerzero,st7789v_lcd`.

The SPI sysfs `modalias` is `SPI_MODULE_PREFIX` + `spi->modalias`
(`drivers/spi/spi.c:57-68`), and `spi_uevent()` emits the same string as
`MODALIAS=spi:<...>` (`drivers/spi/spi.c:399-408`). SPI deliberately uses `spi:`
rather than `of:` modaliases for DT devices. The author's
`grep -h st7789v /sys/bus/spi/devices/*/modalias` output `spi:st7789v_lcd` is
consistent with this.

Module autoloading needs a module alias matching `spi:st7789v_lcd`.
`MODULE_DEVICE_TABLE(spi, panel_mipi_dbi_spi_id)` makes modpost emit
`spi:<name>` for every id-table name (`scripts/mod/file2alias.c:960-968`,
`do_spi_entry()`). Before this PR the table contained only
`panel-mipi-dbi-spi` and `panel-mipi-dbi-m5stack`, so no alias matched
`spi:st7789v_lcd`; adding `{ "st7789v_lcd", 0 }` supplies exactly that alias.
`spi_match_id()` compares the name with `strcmp()`, so the spelling must match
exactly (`drivers/spi/spi.c:346-354`).

The first compatible must stay first: `panel_mipi_dbi_commands_from_fw()` reads
`compatible[0]` and requests `<compatible>.bin`, i.e.
`cardputerzero,st7789v_lcd.bin` (`panel-mipi-dbi-m.c:224-229`). The patch leaves
that path untouched. The driver still binds through the OF table's second
compatible, `panel-mipi-dbi-m5stack`; the new id entry is for autoload, not for
changing the match path.

## 3. Patch assessment

- Scope: 1 file, `+5/-0`; a comment plus one id-table entry. No API, DT, firmware
  name or probe-logic change.
- Placement: the entry is in `panel_mipi_dbi_spi_id[]`, which is the table that
  produces `spi:` aliases. Adding it to `of_match_table` instead would not help,
  because SPI autoload uses the `spi:` modalias.
- Coverage: the repository has exactly two overlays using
  `panel-mipi-dbi-m5stack`, v3 (`:370`) and v5 (`:449`), and both use the same
  first compatible. One entry covers both boards.
- No conflicting user: `panel-mipi-dbi-m5stack` appears only in this module and
  the two Cardputer Zero overlays; `99-cardputer-zero-lcd.rules` only creates the
  DRM card and `/dev/fb_lcd` symlinks, and never modprobes a module.
- Patch hygiene: `git apply --check` passes at base
  `a3fd3e83c0247e16e194e7e40f7fc1f5be933dd4`; the PR is `MERGEABLE` / `clean`.
- No blocking findings. The inline comment says "panels' first compatibles"
  while only one is listed; that is cosmetic, since no other first compatible in
  this repository uses this driver.

## 4. Verification matrix

| Check | Status | Evidence |
| --- | --- | --- |
| Patch scope and apply | `PASS` | 1 file, `+5/-0`; `git apply --check` at base |
| Device modalias rule (first compatible, vendor stripped) | `PASS` (code-level) | 6.1.y `of_modalias_node()`, 6.6.y `of_alias_from_compatible()` |
| SPI uevent / sysfs modalias is `spi:<spi->modalias>` | `PASS` (code-level) | `spi_uevent()`, `modalias_show()` |
| SPI id table produces `spi:<name>` alias | `PASS` (code-level) | `scripts/mod/file2alias.c::do_spi_entry()` |
| Alias name equals observed modalias | `PASS` | `st7789v_lcd` vs author sysfs `spi:st7789v_lcd` |
| First-compatible firmware name preserved | `PASS` | `panel-mipi-dbi-m.c:224-229` unchanged |
| v3 + v5 overlay coverage | `PASS` | both at the same first compatible; only users |
| udev rule does not modprobe | `PASS` | `99-cardputer-zero-lcd.rules` is symlink-only |
| Module rebuild | `NOT RUN` | no Linux kernel headers / cross toolchain |
| Boot-time autoload on Cardputer Zero | `NOT RUN` | no hardware; virtual profile not creatable |
| Author hardware report | `REVIEW` | self-reported on real hardware; not re-run here |
| CI build | `NOT RUN` | only a WeCom digest forwarder workflow |

## 5. Limits

- This record verifies the **mechanism** at source level. It does not observe
  `/dev/fb_lcd`, the console, or `lsmod` on a Cardputer Zero.
- The only runtime evidence is the author's statement in the PR body. It is
  plausible and matches the kernel source, but it was not independently repeated.
- The local Device Service has a `cardputer-zero` profile, but it is
  `supported=false`, `creatable=false`, `backend_ready=false`, with
  `__missing_qemu__` / `__missing_rom__` and a Linux ARM64 backend. No session
  could be created, so virtual-device validation was not possible.
- The hardware bench exposes five ESP32 / ESP32-P4-class nodes; no Cardputer
  Zero, Linux ARM64 or Broadcom target is present.
- No module rebuild was attempted successfully: the host has no Linux ARM64
  kernel headers or cross toolchain. The change is a table-only addition, so the
  absence of a local build does not introduce a code-path uncertainty beyond the
  normal compiler/modpost check.
- The repository has no workflow that builds this module. The only PR check is
  the WeCom digest forwarder, so there is no CI build log to cite.

## 6. Risk and rollback

Risk is low: the entry adds one more alias and one more matchable id name.
A device whose first compatible strips to `st7789v_lcd` would now autoload this
driver; if its `<compatible>.bin` is missing, probe fails with the existing
`request_firmware()` error and no other driver is affected. Rollback is deleting
the five added lines; no state, DT or firmware file changes.

## 7. Reply

One English comment was posted on the PR. It states the code-level evidence,
the kernel file:line references, the NOT RUN runtime items, and the reason
virtual-device validation was not used. The PR was not closed, no branch was
pushed, and no other repository was modified.
