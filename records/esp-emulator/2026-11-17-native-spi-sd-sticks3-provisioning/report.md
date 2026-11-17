# Verify the board-wired storage and provisioning paths

The runs used native Xtensa QEMU SHA-256 `5f8a5f38f0512db04a36fb7ca5cf13ec3d359d0fff1eb481fe9b2c06ab3580f2`. Queued integrated source `20f7e2bece0ace93574b9129576c9b8b14ac71b5` contains the selected SPI and StickS3 changes. The evidence captures the exact isolated service configurations. The StickS3 record separately pins the tested host service modules by SHA-256. This is virtual-device validation of the source behavior.

## SPI SD attach and 96 MiB media

The old service supplied a SPI board's SD media to its SPI controller model and also created a QEMU SDMMC drive for the same file. The SDMMC backend rejected the 96 MiB image before NC1020 ran. The new service supplies media only to the controller wired on the selected board. The power-of-two size rule remains in admission for the modeled SDMMC backend. The FAT32 fixture generator supports the tested 96 MiB geometry with two 512-byte sectors per cluster and computes a sufficient FAT without oscillating at cluster boundaries.

| Case | Result | Actual behavior |
| --- | --- | --- |
| Original NC1020, reference service, 96 MiB author-generated test media | `FAIL` | QEMU start returns `Invalid SD card size: 96 MiB` |
| Exact same original NC1020 and 96 MiB media, corrected service | Mount `PASS`, ROM import `PARTIAL` | 16 of 206 banks observed, 1915 CMD17 commands and no CMD18 |
| Exact original NC1020 and separate 64 MiB one-sector-cluster control | `PARTIAL` | 80 of 206 banks observed, 21800 CMD17 commands and no CMD18 |
| NC1020 with missing ROM or no media | Controls | Missing-ROM run recorded six CMD17 reads, and no-media run recorded zero |
| PaperDIY SDK probe, seeded 96 MiB FAT32 | `PASS` | GPIO48 low, seeded read, write, remount, and `prior=1` after resetting the same session |

The NC1020 runs bound the exact original firmware and author-generated test media, ROM and NOR by hash. They stopped and released their leases. NC1020 startup and save/restore were `NOT RUN`. The two ROM-import observations used different media geometries and provide bounded progress measurements. The PaperDIY run used its own SDK probe and media. It recorded 35 CMD17 reads, 14 CMD24 writes, unchanged uploaded media bytes, a changed writable SD image and a verified ZIP. The guest process and leases cleared after the run. [Storage evidence](evidence/spi-capacity-summary.json)

To reproduce, use `tests/firmware/spi_sd_media` and pinned ESP-IDF v5.5.4. Build PaperDIY with `-DPROBE_PAPERDIY=ON` and its 16 MiB Flash defaults. Generate the FAT32 image and seed it using the fixture instructions.

```sh
python3 platform/tools/sd_image.py --format fat32-mbr --size-mib 96 --sectors-per-cluster 2 --out "$TEST_MEDIA"
```

In a dedicated native Device Service, import the merged image and upload the test media. Create a session with `storage.sd_image_artifact_id` set to the media digest. Verify GPIO48 low for the PaperDIY probe, the UART seed/remount markers, the same-session reset readback and the stopped inventory. Obtain its pre-stop ZIP and independently compare the uploaded digest with the writable session copy. For the NC1020 A/B run, use identical original and media bytes in each service. Compare where startup reaches, watch the SPI command counts, preserve the ZIP before stopping and compare ROM bank progress using the guest output. The archive retains only bounded summaries and hashes of the author-generated material.

## StickS3 provisioning gate

The ESP-IDF probe initially waits on BtnA GPIO11. The wrong-button step delivered BtnB low on GPIO12 while provisioning remained idle. A 350 ms virtual hold on BtnA then produced the GPIO11 low marker before the AP start, application HTTP readiness, association, lease and HTTP sent markers. The private virtual client completed DHCP, ARP and the configured fixed HTTP body check. A same-session reset rearmed the original wait. A fresh BtnA input was required to create the second round. The finalized two-round capture contained two authentication responses, two association responses, two completed DORA exchanges and two bidirectional TCP payload flows.

The separately retained extended no-input control reached the peer DHCP deadline with zero authentication or association responses, zero DORA exchanges, zero bidirectional TCP flows and no fixed HTTP result. The final peer recorded `PARTIAL` at DHCP, which is the expected no-input control observation. The private socketpair used zero host IP backends and cleanup released all leases. [Button and reset cases](evidence/sticks3-button-summary.json) · [Extended zero-input capture](evidence/sticks3-no-input-full-window-summary.json)

Reproduce from `tests/network/native_open_softap` using the pinned ESP-IDF v5.5.4 and `-D M5_FIXTURE_STICKS3_BUTTON=ON`. Run `device_id=sticks3`, `runtime=qemu-wifi`, and `network.profile=sticks3-open-softap-fixture` in an isolated service. Begin each run at `PROVISION_WAIT_BUTTON gpio=11 level=1`. On the wrong-button case submit a 350 ms `button` hold of `b`, require the GPIO12 ignored marker and inspect the idle guest. Submit the same `button` hold for `a` inside the fixture discovery window. Verify the marker order and transport. After reset, wait for the idle marker and repeat the BtnA input. Run another session through the peer DHCP deadline without input. Obtain per-session ZIPs and stop owned sessions, then verify capture finalization and zero leases.

The integrated scope reran the exact PaperDIY 96 MiB probe and StickS3 press/reset case. PaperDIY again read the write after reset. StickS3 again completed two DORA exchanges and two TCP payload flows with input. The receipts preserve the pinned runtime package base, and the executed service-file digests match the integrated source. The reruns supply their own ZIP and capture digests. [Integrated validation](evidence/integrated-rerun-summary.json)

## Scope

StickS3 evidence covers the controlled SDK open provisioning and fixed HTTP path. An original application portal, Linux namespace guest flow, physical hardware and browser WASM were `NOT RUN`. PaperDIY evidence covers attachment at session creation. Hot-plug and physical SD behavior were `NOT RUN`. Rollback returns to the previous service selection logic and fixture capability while retaining existing session state. This record establishes source and virtual-device results. Production rollout and package publication are tracked separately.
