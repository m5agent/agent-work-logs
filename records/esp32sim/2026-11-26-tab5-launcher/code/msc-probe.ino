#include <Arduino.h>
#include <M5Unified.h>

static volatile uint32_t &reg(unsigned offset) {
    return *reinterpret_cast<volatile uint32_t *>(0x50000000u + offset);
}

struct Descriptor { volatile uint32_t status; uint32_t buffer; };
alignas(512) static Descriptor qtd[64];
alignas(64) static uint8_t buffer[512];
static uint8_t address;

static bool wait_for(unsigned offset, uint32_t mask) {
    auto start = millis();
    while (!(reg(offset) & mask) && millis() - start < 2500) delay(1);
    return reg(offset) & mask;
}

static bool transfer(unsigned ep, bool input, bool setup, uint8_t *bytes, size_t len) {
    if (!input && len) memcpy(buffer, bytes, len);
    qtd[0].buffer = reinterpret_cast<uintptr_t>(buffer);
    // IDF v5.5.4 usb_dwc_ll.h: active, end of list, IOC, SETUP and transfer length.
    qtd[0].status = 0x86000000u | (setup ? 1u << 24 : 0) | len;
    reg(0x508) = 0xffffffffu;
    reg(0x510) = 0xff; // one QTD
    reg(0x514) = reinterpret_cast<uintptr_t>(qtd);
    reg(0x500) = 1u << 31 | uint32_t(address) << 22 | (ep ? 2u << 18 : 0) |
        (input ? 1u << 15 : 0) | ep << 11 | (ep ? 512 : 64);
    if (!wait_for(0x508, 2) || (reg(0x508) & 3) != 3 || qtd[0].status != 0) return false;
    if (input && len) memcpy(bytes, buffer, len);
    return true;
}

static bool control(uint8_t type, uint8_t request, uint16_t value, uint8_t *data, uint16_t length) {
    uint8_t setup[8] = {type, request, uint8_t(value), uint8_t(value >> 8), 0, 0, uint8_t(length), uint8_t(length >> 8)};
    if (!transfer(0, false, true, setup, sizeof(setup))) return false;
    if (length && !transfer(0, type & 0x80, false, data, length)) return false;
    return transfer(0, !(type & 0x80), false, nullptr, 0);
}

static bool read_msc() {
    if (reg(0x40) != 0x4f54430a) return false;
    reg(0x0c) = reg(0x0c) | 1u << 29;
    reg(0x08) = 1u << 5; // GAHBCFG.DMAEN
    reg(0x400) = 1u << 23; // HCFG.DESCDMA
    reg(0x440) = 1u << 12; // HPRT.PWR
    if (!wait_for(0x440, 1)) return false;
    reg(0x440) = 1u << 12 | 1u << 8 | 1u << 1; // reset attached device
    delay(60);
    reg(0x440) = 1u << 12;
    if (!wait_for(0x440, 1u << 2)) return false;
    uint8_t device[18], config[32];
    if (!control(0x80, 6, 0x100, device, sizeof(device)) || device[1] != 1) return false;
    if (!control(0, 5, 1, nullptr, 0)) return false;
    address = 1;
    if (!control(0x80, 6, 0x200, config, sizeof(config)) || config[14] != 8 || config[20] != 0x81 || config[27] != 2) return false;
    if (!control(0, 9, 1, nullptr, 0)) return false;
    Serial0.println("MSC_ENUMERATED");
    uint8_t cbw[31] = {'U','S','B','C',1,2,3,4,0,2,0,0,0x80,0,10,0x28,0,0,0,0,4,0,0,1};
    uint8_t sector[512], csw[13];
    return transfer(2, false, false, cbw, sizeof(cbw)) && transfer(1, true, false, sector, sizeof(sector)) &&
        transfer(1, true, false, csw, sizeof(csw)) && memcmp(csw, "USBS\1\2\3\4\0\0\0\0\0", 13) == 0 &&
        memcmp(sector, "ESP32-P4 virtual USB mass storage", 33) == 0;
}

void setup() {
    Serial0.begin(115200);
    M5.begin();
    Serial0.println("MSC_PROBE_READY");
    bool ok = read_msc();
    Serial0.println(ok ? "MSC_READ_SECTOR_4_OK" : "MSC_READ_FAILED");
    M5.Display.fillScreen(ok ? TFT_GREEN : TFT_RED);
    M5.Display.setTextColor(TFT_BLACK);
    M5.Display.setTextSize(4);
    M5.Display.print(ok ? "MSC read OK" : "MSC read failed");
}
void loop() { delay(1000); }
