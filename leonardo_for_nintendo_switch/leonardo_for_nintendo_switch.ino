#include "horipad.h"
#include "cobsr.h"
#include "crc8.h"

#define READ_BUF_SIZE 16
#define READ_TIMEOUT 10

uint8_t read_buf[READ_BUF_SIZE];
uint8_t read_bytes = 0;
uint32_t last_read_millis = 0;

Horipad horipad;

uint8_t buf0[16] = { 0x00, 0x00, 0x0F, 0x80, 0x80, 0x80, 0x80, 0x00 };
uint8_t buf1[16] = { 0x00, 0x00, 0x0F, 0x80, 0x80, 0x80, 0x80, 0x00 };

uint8_t *front_buf = buf0;
uint8_t *back_buf = buf1;

void setup() {
    Serial1.begin(115200);
}

void loop() { 
    if (horipad.ready()) {
        horipad.SendReport(front_buf, 8);
    }

    uint32_t crnt_millis = millis();
   
    if (read_bytes != 0 && crnt_millis - last_read_millis >= READ_TIMEOUT) {
        read_bytes = 0;
    }
    
    if (Serial1.available()) {
        uint8_t incoming_byte = Serial1.read();
        if (incoming_byte != 0) {
            if (read_bytes != READ_BUF_SIZE) {
                read_buf[read_bytes++] = incoming_byte;
                last_read_millis = crnt_millis;
            } else {
                // read buffer overflow
                read_bytes = 0;   
            }
        } else {
            if (read_bytes != 0) {
                size_t len = decode_cobsr(read_buf, read_bytes, back_buf);
                if (!crc8ccitt(back_buf, len)) {
                    uint8_t *tmp = front_buf;
                    front_buf = back_buf;
                    back_buf = tmp;
                } else {
                    // Invalid packet data
                }
                read_bytes = 0;
            }
        }
    }
}
