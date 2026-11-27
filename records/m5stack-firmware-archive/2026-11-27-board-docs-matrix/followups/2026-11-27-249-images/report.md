# Firmware archive publication checkpoint

Arduino CLI 1.3.1 and M5Stack 3.2.5 built each new image in two canonical
work directories. The app, bootloader, partitions, merged image and ELF
matched byte for byte. Private strings scans passed on those artifacts.
This checkpoint includes the native virtual-device replay on esp32sim
`4e257b6be8ee0ed706c2e509d8f31ef7472a424b`. Per-case manifests pin the original and
rebuilt SHA-256, runner inputs, board and checker facts. The preserved
Tab5 original speaker fails compilation at the extra hash on the include
directive. The Atom Echo entries preserve three compilation failures.
The Cardputer-ADV source results preserve the NFC constructor mismatch
and the compatibility variant. Stock UIFlow2 appears as verified external
download URLs and hashes. [Rebuild recipe](https://github.com/m5agent/m5stack-firmware-archive/tree/13483c044b77d66d3a61f01f16fc79a6d4137563/build-records/rebuild-2026-11-27-matrix.md)

| Device | Published | Compiled defect cases | Compile failures indexed | Firmware bytes |
| --- | ---: | ---: | ---: | ---: |
| atom-echo | 0 | 0 | 3 | 0 |
| atom-echos3r | 5 | 0 | 0 | 108338668 |
| atom-lite | 5 | 0 | 0 | 27540308 |
| atom-matrix | 5 | 0 | 0 | 27540308 |
| atom-matrix-v11 | 5 | 0 | 0 | 27540324 |
| atoms3 | 5 | 2 | 0 | 245551324 |
| atoms3-lite | 3 | 1 | 0 | 147390404 |
| atoms3r | 5 | 0 | 0 | 106076284 |
| atoms3r-cam | 1 | 0 | 0 | 22185124 |
| atoms3r-m12 | 1 | 0 | 0 | 22094460 |
| atoms3u | 5 | 0 | 0 | 155930552 |
| atomu | 0 | 0 | 0 | 0 |
| basic-v27 | 9 | 1 | 0 | 50515904 |
| cardputer | 10 | 0 | 0 | 176437808 |
| cardputer-adv | 11 | 0 | 0 | 193896244 |
| core2 | 14 | 0 | 0 | 255317948 |
| cores3 | 15 | 0 | 0 | 452883420 |
| dial | 10 | 0 | 0 | 178990144 |
| m5stick | 0 | 0 | 0 | 0 |
| nanoc6 | 0 | 0 | 0 | 0 |
| nesso-n1 | 0 | 0 | 0 | 0 |
| papercolor | 16 | 2 | 0 | 494054196 |
| paperdiy | 6 | 0 | 0 | 180167076 |
| papermono | 23 | 1 | 0 | 725285624 |
| papers3 | 9 | 0 | 0 | 274838380 |
| stackchan | 26 | 1 | 0 | 835639084 |
| stamplc | 12 | 0 | 1 | 210930380 |
| stickc | 0 | 0 | 0 | 0 |
| stickc-plus | 0 | 0 | 0 | 0 |
| stickc-plus-se | 0 | 0 | 0 | 0 |
| stickc-plus2 | 0 | 0 | 0 | 0 |
| sticks3 | 15 | 5 | 0 | 324075364 |
| stickt2 | 0 | 0 | 0 | 0 |
| stopwatch | 18 | 1 | 0 | 546723484 |
| tab5 | 15 | 0 | 1 | 471761648 |

The firmware bytes column includes distinct archived case files under the
device and excludes the shared boot_app0 asset. The downloadable merged
images and input versions appear in the archived index. The rebuilt cases
have 31 changed PNGs out of
429 comparable frames and
9 changed PCM streams out of
97 comparable streams. The firmware case
manifests contain the paired hashes. Remaining cases are pending at this checkpoint.
Physical hardware validation was NOT RUN.

## Withheld images

| Device | Case | Historical verdict | Rebuilt verdict |
| --- | --- | --- | --- |
| papermono | imu | PASS | FAIL |
| papermono | lora-1 | FAIL | PASS |
| papermono | lora-2 | FAIL | PASS |

The original PaperMono images were replayed on the pinned runtime. LoRa
passed on both original and rebuilt images. The original IMU image passed,
and the rebuilt IMU image failed both runs. The second measurement differed
in 770 of 384,000 decoded pixels. The first measurement and stationary
control matched. [Per-case comparison](evidence/verdict-change-summary.json)
