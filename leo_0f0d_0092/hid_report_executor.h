#include <stdint.h>
#include <string.h>

#include "varint.h"
#include "hid_basic_report.h"

#define BUFFER_SIZE 1024
#define MAX_LOOP_DEPTH 5

uint8_t popcnt(uint8_t bits) {
    bits = (bits & 0x55) + (bits >> 1 & 0x55);
    bits = (bits & 0x33) + (bits >> 2 & 0x33);
    return (bits & 0x0f) + (bits >> 4 & 0x0f);
}

size_t varint_size(const uint8_t *data, size_t size) {
    for (size_t i = 0; i < size; i++) {
        if (!(data[i] & 0x80)) { return i + 1; }
    }
    return 0;
}

size_t instruction_size(uint8_t *buf, size_t buf_size) {
    if (buf_size == 0) { return 0; }
    uint8_t opcode = buf[0];
    if (opcode & 0x80) {
        // complex report (diff from neutral report) + hold time (varint)
        size_t len = popcnt(opcode);
        return len + varint_size(buf + len, buf_size - len);
    } else if (opcode == 0x0e) {
        // loop start (0x0e) + loop count (varint)
        return 1 + varint_size(buf + 1, buf_size - 1);
    } else if (opcode == 0x0f) {
        // loop end (0x0f)
        return 1;
    } else if (0x10 <= opcode && opcode <= 0x7f) {
        // basic report + hold time (varint)
        return 1 + varint_size(buf + 1, buf_size - 1);
    }
    return 0;
}

namespace hidVM {
    enum State { IDLE, EXECUTING };
    State current_state = IDLE;

    uint8_t buf[BUFFER_SIZE];
    uint8_t *end = buf;
    const uint8_t *pos = buf;

    uint32_t hold_time = 0;
    uint32_t hold_start = 0;

    struct Loop { uint32_t count; const uint8_t *start_pos; };
    Loop loop_table[MAX_LOOP_DEPTH];
    uint8_t loop_depth = 0;


    void push(uint8_t *data, int size) {
        if (current_state != IDLE) { return; }
        if (end + size > buf + BUFFER_SIZE) { return; }
        if (instruction_size(data, size) != size) { return; }
        memcpy(end, data, size);
        end += size;
    }

    void clear() {
        if (current_state != IDLE) { return; }
        end = buf;
    }

    void start() {
        if (current_state != IDLE) { return; }
        current_state = EXECUTING;
    }

    void stop() {
        if (current_state != EXECUTING) { return; }
        pos = buf;
        hold_time = 0;
        loop_depth = 0;
        current_state = IDLE;
    }

    bool update(uint8_t *data) {
        if (current_state == IDLE) { return false; }

        if (hold_time != 0) {
            if (millis() - hold_start >= hold_time) {
                hold_time = 0;
            } else { return false; }
        }

        if (pos >= end) {
            current_state = IDLE;
            return false;
        }

        uint8_t opcode = *pos++;
        if ((opcode & 0x80) == 0) {
            switch (opcode) {
                default: return false; // NOT DEFINED
                case 0x0e: // LoopStart
                    if (loop_depth == MAX_LOOP_DEPTH) { return false; }
                    Loop new_loop = loop_table[loop_depth++];
                    pos = decode_varint_u32(pos, end, new_loop.count);
                    if (new_loop.count == 0) { new_loop.count = 1; }
                    new_loop.start_pos = pos;
                    return false;
                case 0x0f: // LoopEnd
                    Loop crnt_loop = loop_table[loop_depth - 1];
                    if (--crnt_loop.count == 0) {
                        loop_depth--;
                    } else {
                        pos = crnt_loop.start_pos;
                    }
                    return false;
                // Basic report
                case 0x10: set_neutral(data); break;

                case 0x11: set_btn_y(data); break;
                case 0x12: set_btn_b(data); break;
                case 0x13: set_btn_a(data); break;
                case 0x14: set_btn_x(data); break;
                case 0x15: set_btn_l(data); break;
                case 0x16: set_btn_r(data); break;
                case 0x17: set_btn_zl(data); break;
                case 0x18: set_btn_zr(data); break;
                case 0x19: set_btn_minus(data); break;
                case 0x1a: set_btn_plus(data); break;
                case 0x1b: set_btn_ls(data); break;
                case 0x1c: set_btn_rs(data); break;
                case 0x1d: set_btn_home(data); break;
                case 0x1e: set_btn_capture(data); break;

                case 0x1f: set_hat_up(data); break;
                case 0x20: set_hat_up_right(data); break;
                case 0x21: set_hat_right(data); break;
                case 0x22: set_hat_down_right(data); break;
                case 0x23: set_hat_down(data); break;
                case 0x24: set_hat_down_left(data); break;
                case 0x25: set_hat_left(data); break;
                case 0x26: set_hat_up_left(data); break;

                case 0x27: set_ls_up(data); break;
                case 0x28: set_ls_up_right(data); break;
                case 0x29: set_ls_right(data); break;
                case 0x2a: set_ls_down_right(data); break;
                case 0x2b: set_ls_down(data); break;
                case 0x2c: set_ls_down_left(data); break;
                case 0x2d: set_ls_left(data); break;
                case 0x2e: set_ls_up_left(data); break;

                case 0x2f: set_rs_up(data); break;
                case 0x30: set_rs_up_right(data); break;
                case 0x31: set_rs_right(data); break;
                case 0x32: set_rs_down_right(data); break;
                case 0x33: set_rs_down(data); break;
                case 0x34: set_rs_down_left(data); break;
                case 0x35: set_rs_left(data); break;
                case 0x36: set_rs_up_left(data); break;
            }
        } else {
            // Complex report (Diff from neutral report)
            if (opcode & 0x01) { data[0] = *pos++; } else { data[0] = 0x00; } // Buttons Low
            if (opcode & 0x02) { data[1] = *pos++; } else { data[1] = 0x00; } // Buttons High
            if (opcode & 0x04) { data[2] = *pos++; } else { data[2] = 0x00; } // HatSwitch
            if (opcode & 0x08) { data[3] = *pos++; } else { data[3] = 0x80; } // LY
            if (opcode & 0x10) { data[4] = *pos++; } else { data[4] = 0x80; } // LY
            if (opcode & 0x20) { data[5] = *pos++; } else { data[5] = 0x80; } // RX
            if (opcode & 0x40) { data[6] = *pos++; } else { data[6] = 0x80; } // RY
        }
        pos = decode_varint_u32(pos, end, hold_time);
        hold_start = millis();
        return true;
    }
}
