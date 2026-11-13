#include <cstdio>

#include "UNIT_8ENCODER.h"

TwoWire Wire;

int main() {
    UNIT_8ENCODER encoder;

    encoder.begin(&Wire, ENCODER_ADDR, 21, 22, 100000UL);
    printf("begin(100000UL) -> wire_begin_frequency=%u\n",
           (unsigned)Wire.last_frequency);
    printf("begin(100000UL) -> sda=%d scl=%d\n", Wire.last_sda, Wire.last_scl);

    encoder.begin(&Wire, ENCODER_ADDR, 21, 22, 400000UL);
    printf("begin(400000UL) -> wire_begin_frequency=%u\n",
           (unsigned)Wire.last_frequency);

    // Keep the pre-existing unchecked-requestFrom observation visible.
    Wire.fail_next_request = true;
    int32_t value = encoder.getEncoderValue(0);
    printf("request_failed: requestFrom_len=%u value=%d\n",
           (unsigned)Wire.last_request_len, (int)value);

    return 0;
}
