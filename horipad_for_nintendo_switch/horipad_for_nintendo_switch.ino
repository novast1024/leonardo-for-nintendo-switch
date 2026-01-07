#include "horipad.h"

Horipad horipad;

uint8_t buf0[8] = { 0x00, 0x00, 0x08, 0x80, 0x80, 0x80, 0x80, 0x00 };
uint8_t buf1[8] = { 0x00, 0x00, 0x08, 0x80, 0x80, 0x80, 0x80, 0x00 };

uint8_t *crnt_buf = buf0;
uint8_t *next_buf =  buf1;

#define MAX_REPORT_INTERVAL 8
uint32_t last_report_millis = 0;

#define READ_TIMEOUT 10
uint32_t last_read_millis = 0;
uint8_t read_bytes = 0;

void setup() {
    Serial1.begin(115200);
    last_report_millis = millis();
}

void loop() {
    uint32_t crnt_millis = millis();

    if (read_bytes != 0 && crnt_millis - last_read_millis >= READ_TIMEOUT) {
        read_bytes = 0;
    }
    
    if (Serial1.available()) {
        next_buf[read_bytes++] = Serial1.read();
        last_read_millis = crnt_millis;

        if (read_bytes == 8) {
            read_bytes = 0;
            
            uint8_t *tmp = crnt_buf;
            crnt_buf = next_buf;
            next_buf = tmp;
            
            horipad.SendReport(crnt_buf, 8);
            last_report_millis = crnt_millis;
        }
    }
    
    if (crnt_millis - last_report_millis >= MAX_REPORT_INTERVAL) {
        horipad.SendReport(crnt_buf, 8);
        last_report_millis = crnt_millis;
    }
}
