#include <Arduino.h>
#include <M5Unified.h>
#include "usb/usb_host.h"

static usb_host_client_handle_t client;
static usb_device_handle_t device;
static uint8_t address;
static bool done;

static void client_event(const usb_host_client_event_msg_t *msg, void *) {
    if (msg->event == USB_HOST_CLIENT_EVENT_NEW_DEV) address = msg->new_dev.address;
}

static void library(void *) {
    for (;;) {
        uint32_t flags;
        usb_host_lib_handle_events(portMAX_DELAY, &flags);
    }
}

static void completed(usb_transfer_t *t) {
    done = true;
    if (t->status != USB_TRANSFER_STATUS_COMPLETED) Serial0.printf("USB transfer failed %d\n", int(t->status));
}

static bool bulk(uint8_t ep, unsigned char *bytes, size_t len) {
    usb_transfer_t *t;
    if (usb_host_transfer_alloc(512, 0, &t) != ESP_OK) return false;
    t->device_handle = device;
    t->bEndpointAddress = ep;
    t->num_bytes = (ep & 0x80) ? 512 : len;
    t->callback = completed;
    if (!(ep & 0x80)) memcpy(t->data_buffer, bytes, len);
    done = false;
    ESP_ERROR_CHECK(usb_host_transfer_submit(t));
    auto started = millis();
    while (!done && millis() - started < 2000) usb_host_client_handle_events(client, pdMS_TO_TICKS(50));
    if (!done) return false;
    bool ok = t->status == USB_TRANSFER_STATUS_COMPLETED && size_t(t->actual_num_bytes) == len;
    if (ok && (ep & 0x80)) memcpy(bytes, t->data_buffer, len);
    ESP_ERROR_CHECK(usb_host_transfer_free(t));
    return ok;
}

void setup() {
    Serial0.begin(115200);
    Serial0.println("MSC_PROBE_BEFORE_M5");
    M5.begin();
    Serial0.println("MSC_PROBE_BEFORE_HOST");
    usb_host_config_t host = {};
    host.skip_phy_setup = true;
    ESP_ERROR_CHECK(usb_host_install(&host));
    xTaskCreate(library, "usb-events", 4096, nullptr, 4, nullptr);
    usb_host_client_config_t config = {};
    config.max_num_event_msg = 8;
    config.async.client_event_callback = client_event;
    ESP_ERROR_CHECK(usb_host_client_register(&config, &client));
    Serial0.println("MSC_PROBE_READY");
}

void loop() {
    usb_host_client_handle_events(client, pdMS_TO_TICKS(50));
    if (!address || device) return;
    ESP_ERROR_CHECK(usb_host_device_open(client, address, &device));
    const usb_config_desc_t *config;
    ESP_ERROR_CHECK(usb_host_get_active_config_descriptor(device, &config));
    const uint8_t *b = reinterpret_cast<const uint8_t *>(config);
    if (config->wTotalLength != 32 || b[14] != 8 || b[18 + 2] != 0x81 || b[25 + 2] != 2) {
        Serial0.println("MSC_BAD_CONFIGURATION");
        return;
    }
    ESP_ERROR_CHECK(usb_host_interface_claim(client, device, 0, 0));
    Serial0.println("MSC_ENUMERATED");
    uint8_t cbw[31] = {'U','S','B','C',1,2,3,4,0,2,0,0,0x80,0,10,0x28,0,0,0,0,4,0,0,1};
    uint8_t sector[512], csw[13];
    if (bulk(2, cbw, sizeof(cbw)) && bulk(0x81, sector, sizeof(sector)) && bulk(0x81, csw, sizeof(csw)) &&
        memcmp(csw, "USBS\1\2\3\4\0\0\0\0\0", 13) == 0 &&
        memcmp(sector, "ESP32-P4 virtual USB mass storage", 33) == 0) {
        Serial0.println("MSC_READ_SECTOR_4_OK");
        M5.Display.fillScreen(TFT_GREEN);
        M5.Display.setTextColor(TFT_BLACK);
        M5.Display.setTextSize(4);
        M5.Display.print("MSC read OK");
    } else {
        Serial0.println("MSC_READ_FAILED");
        M5.Display.fillScreen(TFT_RED);
    }
}
