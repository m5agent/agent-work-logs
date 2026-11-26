| Case | Verdict | Evidence |
| --- | --- | --- |
| display | PASS | multicolored circles and rectangles change |
| quickstart-bargraph | PASS | colored columns and white peaks animate |
| touch | PASS | flick/release, coordinates and green point |
| button | PASS | 250 ms key press displays Btn PWR |
| power | PASS | battery 4123→3678 mV, 87→42%, VBUS 5000→0 mV |
| imu | PASS | two injected vectors on LCD (HWCDC uninitialized by sketch) |
| ltr553 | PASS | PS 321→1456, ALS 260→1440 (HWCDC uninitialized by sketch) |
| rtc | PASS | associated AP, NTP reply, RTC/system/local time advance |
| speaker | PASS | vertical title and 3× each of 10 kHz / 4 kHz |
| mic | PASS | REC waveform → PLAY, 733.09 Hz, RMS 946.8 |
| camera | PASS | two asymmetric mirrored RGB565 fixtures, zero dropped frames |
| wakeup | PASS | black asleep, RTC expiration, PMIC restart and restored UI |
| sdcard | PASS | FAT32 WriteTest.txt matches and both PNGs render byte-for-byte |
| pic | PASS | FAT32 WriteTest.txt matches and both PNGs render byte-for-byte |
| wav | PASS | SD reads, 12 s of 440/660 Hz audio and USB completion marker |

15/15 passed
