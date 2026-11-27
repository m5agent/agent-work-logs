# esp32sim rollout by device

All native results are virtual-device validation. Stock boot means the Device Service lease reached running and stopped. The docs and UIFlow2 fixture counts describe observed starts and stops. Full application and peripheral parity requires case-specific oracles and deterministic repeats.

| Device | Native default | Stock boot esp32sim / QEMU | Arduino docs boots esp32sim / QEMU | Checked-in UIFlow2 fixture boots | esp32sim WASM | QEMU-WASM public profile |
| --- | --- | --- | --- | --- | --- | --- |
| Atom Echo | QEMU | PASS / PASS | NOT RUN / NOT RUN | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Outside the public export |
| Atom VoiceS3R | QEMU | PASS / PASS | 5/5 / 5/5 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Outside the public export |
| Atom Lite | QEMU | PASS / PASS | 5/5 / 5/5 | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Available |
| Atom Matrix | QEMU | PASS / PASS | 5/5 / 5/5 | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Available |
| Atom Matrix v1.1 | QEMU | PASS / PASS | 5/5 / 5/5 | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Available |
| AtomS3 | QEMU | PASS / PASS | 5/5 / 5/5 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| AtomS3 Lite | QEMU | PASS / PASS | 3/3 / 3/3 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| AtomS3R | QEMU | PASS / PASS | 5/5 / 5/5 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| AtomS3R-CAM | QEMU | PASS / PASS | 1/1 / 1/1 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Outside the public export |
| AtomS3R-M12 | QEMU | PASS / PASS | 1/1 / 1/1 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Outside the public export |
| AtomS3U | QEMU | PASS / PASS | 5/5 / 5/5 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Outside the public export |
| AtomU | QEMU | PASS / PASS | NOT RUN / NOT RUN | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Outside the public export |
| Basic v2.7 | QEMU | PASS / PASS | 9/9 / 9/9 | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Outside the public export |
| Cardputer | QEMU | PASS / PASS | 10/10 / 10/10 | NOT RUN | PASS in exported workbench | Available |
| Cardputer-ADV | esp32sim | PASS / PASS | NOT RUN / NOT RUN | 2/2 | PASS in exported workbench | Available |
| CardputerZero | External Linux | NOT RUN / NOT RUN | NOT RUN / NOT RUN | NOT RUN | NOT RUN. Separate Linux backend | Outside the public export |
| Core2 | QEMU | PASS / PASS | 14/14 / 14/14 | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Available |
| CoreS3 | esp32sim | PASS / PASS | NOT RUN / NOT RUN | 2/2 | PASS in exported workbench | Available |
| Dial | QEMU | PASS / PASS | 10/10 / 10/10 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Outside the public export |
| M5Stick | Explicit esp32sim required | PASS / NOT RUN | NOT RUN / NOT RUN | NOT RUN | NOT RUN. Classic ROM routing and Flash offset admission pending | Outside the public export |
| NanoC6 | QEMU | PASS / PASS | 15/15 / 15/15 | 2/2 | NOT RUN. C6 ROM routing and board admission pending | Outside the public export |
| Arduino Nesso N1 | QEMU | PASS / PASS | 11/11 / 11/11 | 2/2 | NOT RUN. C6 ROM routing and board admission pending | Outside the public export |
| PaperColor | QEMU | PASS / PASS | 16/16 / 16/16 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| PaperDIY | QEMU | PASS / PASS | 6/6 / 6/6 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| PaperMono | QEMU | PASS / PASS | 26/26 / 26/26 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| PaperS3 | QEMU | PASS / PASS | 9/9 / 9/9 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| StackChan | QEMU | PASS / PASS | 26/26 / 26/26 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| StamPLC | QEMU | PASS / PASS | 12/12 / 12/12 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| StickC | QEMU | PASS / PASS | 37/38 / 38/38 | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Available |
| StickC Plus | QEMU | PASS / PASS | 28/29 / 29/29 | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Available |
| StickC Plus SE | QEMU | PASS / PASS | 8/8 / 8/8 | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Available |
| StickC Plus2 | QEMU | PASS / PASS | 10/10 / 10/10 | 2/2 | NOT RUN. Classic ROM routing and Flash offset admission pending | Available |
| StickS3 | QEMU | PASS / PASS | 15/15 / 15/15 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| M5StickT2 | Explicit esp32sim required | PASS / NOT RUN | NOT RUN / NOT RUN | NOT RUN | NOT RUN. Classic ROM routing and Flash offset admission pending | Outside the public export |
| StopWatch | QEMU | PASS / PASS | 18/18 / 18/18 | 2/2 | NOT RUN. Exact workbench profile, guest input/output and Worker teardown evidence pending | Available |
| Tab5 | esp-emu or qualified esp32sim pair | PASS / PASS | NOT RUN / NOT RUN | NOT RUN | NOT RUN. P4 ROM revision and C6 co-processor asset loading pending | Outside the public export |

## Limits

The QEMU-WASM column is the public-profile inventory of the prepared Pages export. The esp32sim WASM column records completed guest validations.
M5Stick and StickT2 have no QEMU Device Service counterpart in the current firmware/kernel modes. CardputerZero has no ESP32 firmware path.
The stock launcher on the GitHub v2.5.4 AtomU and Atom Echo images aborts at the missing M5Things import. A REPL prompt after that abort does not qualify the launcher.
The StickC `axp192_m5stickc-3` and StickC Plus `power-3` esp32sim sessions reported running and subsequently failed before a confirmed clean stop. The paired QEMU sessions stopped cleanly.
Fixture composition requires a matching stock UIFlow2 image and checked-in files directory. Unpaired fixture rows, missing docs firmware and unbuilt docs examples are NOT RUN.
The native comparison uses the radio-sync source build with the checked-in service control overlay. Existing standalone radio pairing evidence remains separate from Device Service.

## QEMU baseline binaries

- qemu_xtensa `04abc3ba8cb115919e7faebd55425c802f4f6e40b10bc3cc422c51700add728e`
- qemu_c6 `69493c4edccaab5bc24961982ddb9097dda11c9b3418f9cdc0aaa2b27ae865a4`
- tab5_esp_emu_dsi `633a35f993300a765634ed78a2dbcfd5ffcd5c3f2f354a2dddabeb6108240828`
