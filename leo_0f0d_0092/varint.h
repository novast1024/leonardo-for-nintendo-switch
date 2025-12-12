#include <stdint.h>
#include <string.h>

// Encode an unsigned 32-bit integer to varint.
// Returns number of bytes written (1-5).
// buf must have space for at least 5 bytes.
size_t encode_varint_u32(uint32_t value, uint8_t *buf) {
    size_t i = 0;
    while (value >= 0x80) {
        buf[i++] = (uint8_t)(value & 0x7f | 0x80);
        value >>= 7;
    }
    buf[i++] = (uint8_t)(value & 0x7F);
    return i;
}


// Decode a 32-bit unsigned integer from Varint format.
// Returns pointer to the next byte (end pointer).
// Updates 'result' by reference.
const uint8_t * decode_varint_u32(const uint8_t *data, const uint8_t *end, uint32_t &result) {
    result = 0;
    size_t shift = 0;
    const uint8_t *pos = data;
    while (pos < end && shift < 32) {
        uint8_t byte = *pos++;
        result |= static_cast<uint32_t>(byte & 0x7F) << shift;
        if ((byte & 0x80) == 0) { return pos; }
        shift += 7;
    }
    return pos; // Return pointer at error/partial decode
}