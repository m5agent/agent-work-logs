#include <M5Unified.h>

static void report(const char* step) {
    auto pa = M5.getIOExpander(0).getWriteValue(2);
    auto usb = M5.getIOExpander(1).getWriteValue(3);
    Serial0.printf("TAB5_RAIL %s PA=%d USB=%d\n", step, int(pa), int(usb));
}

void setup() {
    Serial0.begin(115200);
    M5.begin();
    M5.Power.setExtOutput(true);
    report("both");
    M5.Power.setExtOutput(false, m5::ext_port_mask_t::ext_PA);
    report("no-pa");
    M5.Power.setExtOutput(false, m5::ext_port_mask_t::ext_USB);
    report("neither");
}

void loop() { delay(1000); }
