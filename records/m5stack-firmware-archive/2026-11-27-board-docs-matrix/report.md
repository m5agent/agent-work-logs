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
download URLs and hashes. [Rebuild recipe](https://github.com/m5agent/m5stack-firmware-archive/tree/0bbb597ad7686068d8fab52dacafafdbab98af75/build-records/rebuild-2026-11-27-matrix.md)

| Device | Published | Compiled defect cases | Compile failures indexed | Firmware bytes |
| --- | ---: | ---: | ---: | ---: |
| atom-echo | 0 | 0 | 3 | 0 |
| atom-echos3r | 0 | 0 | 0 | 0 |
| atom-lite | 0 | 0 | 0 | 0 |
| atom-matrix | 0 | 0 | 0 | 0 |
| atom-matrix-v11 | 0 | 0 | 0 | 0 |
| atoms3 | 0 | 0 | 0 | 0 |
| atoms3-lite | 0 | 0 | 0 | 0 |
| atoms3r | 0 | 0 | 0 | 0 |
| atoms3r-cam | 1 | 0 | 0 | 22185124 |
| atoms3r-m12 | 1 | 0 | 0 | 22094460 |
| atoms3u | 0 | 0 | 0 | 0 |
| atomu | 0 | 0 | 0 | 0 |
| basic-v27 | 0 | 0 | 0 | 0 |
| cardputer | 3 | 0 | 0 | 53206848 |
| cardputer-adv | 11 | 0 | 0 | 193896244 |
| core2 | 0 | 0 | 0 | 0 |
| cores3 | 15 | 0 | 0 | 452883420 |
| dial | 0 | 0 | 0 | 0 |
| m5stick | 0 | 0 | 0 | 0 |
| nanoc6 | 0 | 0 | 0 | 0 |
| nesso-n1 | 0 | 0 | 0 | 0 |
| papercolor | 0 | 0 | 0 | 0 |
| paperdiy | 0 | 0 | 0 | 0 |
| papermono | 0 | 0 | 0 | 0 |
| papers3 | 0 | 0 | 0 | 0 |
| stackchan | 0 | 0 | 0 | 0 |
| stamplc | 0 | 0 | 0 | 0 |
| stickc | 0 | 0 | 0 | 0 |
| stickc-plus | 0 | 0 | 0 | 0 |
| stickc-plus-se | 0 | 0 | 0 | 0 |
| stickc-plus2 | 0 | 0 | 0 | 0 |
| sticks3 | 0 | 0 | 0 | 0 |
| stickt2 | 0 | 0 | 0 | 0 |
| stopwatch | 0 | 0 | 0 | 0 |
| tab5 | 15 | 0 | 1 | 471761648 |

The firmware bytes column includes distinct archived case files under the
device and excludes the shared boot_app0 asset. The downloadable merged
images and input versions appear in the archived index. Remaining cases
are pending at this checkpoint. Physical hardware validation was NOT RUN.
