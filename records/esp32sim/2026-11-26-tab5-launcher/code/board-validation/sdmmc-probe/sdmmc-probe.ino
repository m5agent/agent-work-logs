#include <M5Unified.h>
#include <SD_MMC.h>
#include <cstring>

void setup() {
    Serial0.begin(115200);
    M5.begin();
    if (!SD_MMC.setPins(43, 44, 39, 40, 41, 42) || !SD_MMC.begin("/sdcard", false)) {
        Serial0.println("TAB5_SDMMC_MOUNT_FAIL");
        return;
    }

    constexpr char expected[] = "Hello, world! \nSD card write success! \n";
    char received[sizeof(expected) - 1];
    auto test = SD_MMC.open("/WriteTest.txt", FILE_READ);
    if (!test || test.readBytes(received, sizeof(received)) != sizeof(received)
        || test.available() || std::memcmp(expected, received, sizeof(received))) {
        Serial0.println("TAB5_SDMMC_READ_FAIL");
        return;
    }

    Serial0.println("TAB5_SDMMC_SPI_FILE_OK");
    M5.Display.fillScreen(0x07e0);
}
void loop() { delay(1000); }
