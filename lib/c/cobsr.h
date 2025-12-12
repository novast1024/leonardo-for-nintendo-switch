#include <stdint.h>
#include <string.h>

/**
 * Encode a byte sequnce using Consistent Overhead Byte Stuffing / Reduced (COBS/R).
 */
size_t encode_cobsr(
    uint8_t *input, size_t input_size,
    uint8_t *output, size_t output_size
) {
    if (input_size == 0 && output_size != 0) {
        output[0] = 0x01;
        return 1;
    }

    size_t write_index = 1;
    size_t code_index = 0;
    uint8_t code = 1; // Distance to the next zero or block boundary

    for (size_t i = 0; i < input_size; i++) {
        uint8_t byte = input[i];

        if (byte != 0) {
            output[write_index++] = byte;
            code++;
            if (code == 0xFF) {
                goto close_block;
            }
        } else {
            close_block:
            // Finalize the current code (i.e. close the block)
            // and start a new block
            output[code_index] = code;
            code_index = write_index++;
            code = 1;
        }
    }

    // --- COBS/R optimization ---
    // If the last input byte is greater than or equal to the final code value,
    // it can replace the code byte directly, and the redundant last byte
    // can be remove from the sequence.
    uint8_t last = output[write_index - 1];
    if (last >= code) {
        output[code_index] = last;
        write_index--;
    } else {
        output[code_index] = code;
    }
    return write_index;
}

/**
 * Decode a byte sequence encoded with Consistent Overhead Byte Stuffing/Reduced (COBS/R)
 */
size_t decode_cobsr(
    uint8_t *input, size_t input_size,
    uint8_t *output, size_t output_size
) {
    if (input_size == 0) { return 0; }

    size_t write_index = 0;
    size_t code_index = 0;
    while (true) {
        uint8_t code = input[code_index];
        size_t remaining_bytes = input_size - code_index;
        if (code > input_size - code_index) {
            memcpy(output + write_index, input + code_index + 1, remaining_bytes - 1);
            write_index += remaining_bytes - 1;
            output[write_index++] += code;
            break;
        } else {
            memcpy(output + write_index, input + code_index + 1, code - 1);
            code_index += code;
            write_index += code - 1;
            if (code_index == input_size) {
                break;
            }
            if (code != 0xFF) {
                output[write_index++] = 0x00;
            }
        }
    }
    return write_index;
}