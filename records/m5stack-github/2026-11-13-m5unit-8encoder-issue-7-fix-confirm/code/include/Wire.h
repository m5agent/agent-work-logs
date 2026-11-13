#pragma once
#include <cstdint>
#include <cstddef>

// Recording mock: captures the frequency handed to Wire.begin() and lets the
// test force requestFrom() to fail, so the library logic can be observed
// without any Arduino core or hardware.
class TwoWire {
   public:
    uint32_t last_frequency = 0;
    int last_sda = -1;
    int last_scl = -1;
    uint8_t last_request_len = 0;
    bool fail_next_request = false;
    bool request_failed = false;

    bool begin(int sda = -1, int scl = -1, uint32_t frequency = 0) {
        last_sda = sda;
        last_scl = scl;
        last_frequency = frequency;
        return true;
    }
    void beginTransmission(uint8_t) {}
    size_t write(uint8_t) { return 1; }
    uint8_t endTransmission() { return 0; }
    size_t requestFrom(uint8_t, uint8_t len) {
        last_request_len = len;
        if (fail_next_request) {
            fail_next_request = false;
            request_failed = true;
            return 0;
        }
        return len;
    }
    int read() { return 0xFF; }
};

extern TwoWire Wire;
