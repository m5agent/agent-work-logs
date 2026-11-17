# ESP32-S3 BBPLL startup and combined runtime retest

Date 2026-11-17. Virtual-device validation. Overall PARTIAL across the recorded scope.

CPU live sampling located the original ESP-IDF v6.1.1 startup stall in BBPLL calibration. The BBPLL-only runtime allowed the unchanged Cardputer image to reach the application and complete LittleFS. A separate combined runtime completed six LittleFS cases across ESP-IDF v5.5.4 and v6.1.1. Core2 watchdog evidence was also repeated on the combined native QEMU build.

- [Cause, fix, execution boundaries and reproduction](report.md)
- [Structured run record](run.json)
- [Original failure and BBPLL-only control](evidence/bbpll-6-1-source-summary.json)
- [Combined LittleFS evidence](evidence/combined-littlefs-summary.json)
- [Combined Core2 watchdog evidence](evidence/combined-core2-watchdog-summary.json)
- [Separate combined Cardputer ADV SoftAP replay](../../../2026-11-17-isolated-native-open-softap/evidence/combined-adv-reset-summary.json)
