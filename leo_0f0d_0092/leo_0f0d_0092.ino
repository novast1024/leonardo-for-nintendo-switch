#ifndef __AVR_ATmega32U4__
#define __AVR_ATmega32U4__
#endif

#include <stdint.h>
#include <string.h>
#include <Arduino.h>
#include <HID.h>



// ===== Gamepad HID =====

static const uint8_t HID_REPORT_DESCRIPTOR[86] PROGMEM = {
    0x05, 0x01, 0x09, 0x05, 0xa1, 0x01, 0x15, 0x00, 0x25, 0x01,
    0x35, 0x00, 0x45, 0x01, 0x75, 0x01, 0x95, 0x10, 0x05, 0x09,
    0x19, 0x01, 0x29, 0x10, 0x81, 0x02, 0x05, 0x01, 0x25, 0x07,
    0x46, 0x3b, 0x01, 0x75, 0x04, 0x95, 0x01, 0x65, 0x14, 0x09,
    0x39, 0x81, 0x42, 0x65, 0x00, 0x95, 0x01, 0x81, 0x01, 0x26,
    0xff, 0x00, 0x46, 0xff, 0x00, 0x09, 0x30, 0x09, 0x31, 0x09,
    0x32, 0x09, 0x35, 0x75, 0x08, 0x95, 0x04, 0x81, 0x02, 0x06,
    0x00, 0xff, 0x09, 0x20, 0x95, 0x01, 0x81, 0x02, 0x0a, 0x21,
    0x26, 0x95, 0x08, 0x91, 0x02, 0xc0
};

class MyHID : public HID_ {
public:
    int SendReport(const void *data, int len) {
        auto ret = USB_Send(pluggedEndpoint | TRANSFER_RELEASE, data, len);
        return ret;
    }
};

MyHID hid;

void initHID() {
    HIDSubDescriptor node(HID_REPORT_DESCRIPTOR, sizeof(HID_REPORT_DESCRIPTOR));
    hid.AppendDescriptor(&node);
}

// ===== Parse Serial Data =====


uint8_t report[] = {0,0,8,128,128,128,128,0};

#define TIMEOUT 10

unsigned long start_time;


#define BUFFER_SIZE 32
uint8_t buffer[BUFFER_SIZE];

void setup() {
    Serial1.begin(9600);
    initHID();
}

#define DELIMITER 0x00
#define MAX_PACKET_SIZE 32

uint8_t packet[MAX_PACKET_SIZE];
uint8_t packet_size = 0;

void loop() {
    if (Serial1.available()) {
        uint8_t byte = Serial1.read();
        if (byte != DELIMITER) {
            if (packet_size != MAX_PACKET_SIZE) {
                packet[packet_size++] = byte;
            } else {
                // exceeds maximal packet size
            }
        } else if (packet_size != 0) {
            // parse packet
        }
    }
    // macro::update();
}
