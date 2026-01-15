#ifndef COBSR_H
#define COBSR_H

#include <stdint.h>
#include <string.h>

/**
 * Encode a byte sequnce using Consistent Overhead Byte Stuffing / Reduced (COBS/R).
 *
 * NOTE:
 *   The output buffer must be at least (in_size + in_size / 254 + 1) bytes long.
 */
size_t encode_cobsr(const uint8_t *in, size_t in_size, uint8_t *out) {
    if (in_size == 0) {
        out[0] = 0x01;
        return 1;
    }

    size_t write_index = 1;
    size_t code_index = 0;
    uint8_t code = 1; // Distance to the next zero or block boundary

    for (size_t i = 0; i < in_size; i++) {
        uint8_t byte = in[i];

        if (byte != 0) {
            out[write_index++] = byte;
            code++;
            if (code == 0xFF) {
                goto close_block;
            }
        } else {
            close_block:
            // Finalize the current code (i.e. close the block)
            // and start a new block
            out[code_index] = code;
            code_index = write_index++;
            code = 1;
        }
    }

    // --- COBS/R optimization ---
    // If the last input byte is greater than or equal to the final code value,
    // it can replace the code byte directly, and the redundant last byte
    // can be remove from the sequence.
    uint8_t last = out[write_index - 1];
    if (last >= code) {
        out[code_index] = last;
        write_index--;
    } else {
        out[code_index] = code;
    }
    return write_index;
}

/**
 * Decode a COBS/R-encoded byte sequence.
 *
 * NOTE:
 *   The output buffer must be at least (in_end - in_begin) bytes long.
 *   COBS/R decoding never produces more output than input.
 */
size_t decode_cobsr(const uint8_t *in, size_t in_size, uint8_t *out) {
    if (in_size == 0) { return 0; }

    const uint8_t *in_end = in + in_size;
    const uint8_t *in_pos = in; // position of the current code byte
    uint8_t *out_pos = out;

    while (true) {
        uint8_t code = *in_pos;
        size_t remaining = (size_t)(in_end - in_pos);
        if (code > remaining) {
            // The final block with 1-byte reduction
            memcpy(out_pos, in_pos + 1, remaining - 1);
            out_pos += remaining - 1;
            *out_pos++ = code;
            break;
        }
        memcpy(out_pos, in_pos + 1, code - 1);
        out_pos += code - 1;
        in_pos += code;
        if (in_pos == in_end) {
            // the current block is final (same as standard COBS)
            break;
        }
        if (code != 0xFF) {
            // Insert a zero before next block
            *out_pos++ = 0x00;
        }
    }
    return (size_t)(out_pos - out);
}

#endif