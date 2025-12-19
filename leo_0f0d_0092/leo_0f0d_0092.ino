#ifndef __AVR_ATmega32U4__
#define __AVR_ATmega32U4__
#endif

#include <stdint.h>
#include <string.h>
#include <Arduino.h>
#include <HID.h>

#include "hid_report_executor.h"
#include "cobsr.h"
#include "crc8.h"


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

// 115200 bps

void setup() {
    Serial1.begin(115200);
    initHID();
}

#define DELIMITER 0x00
#define MAX_PACKET_SIZE 32

uint8_t encoded[MAX_PACKET_SIZE];
uint8_t decoded[MAX_PACKET_SIZE];
uint8_t encoded_size = 0;
uint8_t decoded_size = 0;

void parse(uint8_t *data, uint8_t size) {
    uint8_t *pos = data;
    uint8_t opcode = *pos++;

    if (!(opcode & 0x80)) {
        switch (opcode) {
            case 0x01: hidVM::push(pos, size - 1);
            case 0x02:

            case 0x10: set_neutral(data);

            case 0x11: set_btn_y(data);
            case 0x12: set_btn_b(data);
            case 0x13: set_btn_a(data);
            case 0x14: set_btn_x(data);
            case 0x15: set_btn_l(data);
            case 0x16: set_btn_r(data);
            case 0x17: set_btn_zl(data);
            case 0x18: set_btn_zr(data);
            case 0x19: set_btn_minus(data);
            case 0x1a: set_btn_plus(data);
            case 0x1b: set_btn_ls(data);
            case 0x1c: set_btn_rs(data);
            case 0x1d: set_btn_home(data);
            case 0x1e: set_btn_capture(data);

            case 0x1f: set_hat_up(data);
            case 0x20: set_hat_up_right(data);
            case 0x21: set_hat_right(data);
            case 0x22: set_hat_down_right(data);
            case 0x23: set_hat_down(data);
            case 0x24: set_hat_down_left(data);
            case 0x25: set_hat_left(data);
            case 0x26: set_hat_up_left(data);

            case 0x27: set_ls_up(data);
            case 0x28: set_ls_up_right(data);
            case 0x29: set_ls_right(data);
            case 0x2a: set_ls_down_right(data);
            case 0x2b: set_ls_down(data);
            case 0x2c: set_ls_down_left(data);
            case 0x2d: set_ls_left(data);
            case 0x2e: set_ls_up_left(data);

            case 0x2f: set_rs_up(data);
            case 0x30: set_rs_up_right(data);
            case 0x31: set_rs_right(data);
            case 0x32: set_rs_down_right(data);
            case 0x33: set_rs_down(data);
            case 0x34: set_rs_down_left(data);
            case 0x35: set_rs_left(data);
            case 0x36: set_rs_up_left(data);
            default: break;
        }
    } else {
        if (opcode & 0x01) { report[0] = data[1]; } else { report[0] = 0x00; }
        if (opcode & 0x02) { report[1] = data[1]; } else { report[1] = 0x00; }
        if (opcode & 0x04) { report[2] = data[1]; } else { report[2] = 0x08; }
        if (opcode & 0x08) { report[3] = data[1]; } else { report[3] = 0x80; }
        if (opcode & 0x10) { report[4] = data[1]; } else { report[4] = 0x80; }
        if (opcode & 0x20) { report[5] = data[1]; } else { report[5] = 0x80; }
        if (opcode & 0x40) { report[6] = data[1]; } else { report[6] = 0x80; }
    }
}

void loop() {
    if (Serial1.available()) {
        uint8_t byte = Serial1.read();
        if (byte != DELIMITER) {
            if (encoded_size < MAX_PACKET_SIZE) {
                encoded[encoded_size++] = byte;
            } else {
                // exceeds maximal packet size
                encoded_size = 0;
            }
        } else if (encoded_size != 0) {
            decoded_size = decode_cobsr(encoded, encoded_size, decoded);
            if (crc8ccitt(decoded, decoded_size) == 0 && decoded_size > 2) {
                parse(decoded, decoded_size - 1);
            }
            encoded_size = 0;
        }
    }
    hidVM::update(report);
    hid.SendReport(report, 8);
}
