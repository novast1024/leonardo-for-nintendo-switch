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
//
// Input data is assumed to be valid (CRC checked).
// Therefore, only minimal safety checks are included:
// - buffer bounds
// - shift limit
uint32_t decode_varint_u32(const uint8_t *data, size_t size, size_t &offset) {
    uint32_t result = 0;
    size_t shift = 0;
    while (offset < size && shift < 32) {
        uint8_t byte = data[offset++];
        result |= static_cast<uint32_t>(byte & 0x7F) << shift;
        if ((byte & 0x80) == 0) {
            return result;
        }
        shift += 7;
    }
    return result; // Return the partially decoded value on error.
}

// size_t encode_varint(uint32_t value, uint8_t *buf, size_t buf_size) {
//     for (size_t i = 0; i < buf_size; ++i) {
//         uint8_t payload = value & 0x7F;
//         value >>= 7;
//         if (value) {
//             buf[i] = payload | 0x80; // continuation bit
//         } else {
//             buf[i] = payload;
//             return i + 1;
//         }
//     }
//     return 0; // buffer overflow
// }

// bool decode_varint_u32(const uint8_t *data, size_t size, size_t &offset, uint32_t &result) {
//     result = 0;
//     uint8_t shift = 0;
//     while (offset < size) {
//         uint8_t byte = data[offset++];
//         result |= (byte & 0x7f) << shift;
//         if (!(byte & 0x80)) { return true; }
//         shift += 7;
//     }
//     return false;
// }