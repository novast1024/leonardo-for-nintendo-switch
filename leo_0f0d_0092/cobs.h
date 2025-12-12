#ifndef COBS_H
#define COBS_H
#include <stdint.h>
#include <stddef.h>



// Consistent Overhead Byte Stuffing - Reduced
namespace cobsr {
    inline int max_encoded_size(size_t size) { return size + size / 254 + 1; }

    inline size_t encode(const uint8_t* src, size_t src_size, uint8_t* dst) {
        if (!src_size) { return 0; }

        uint8_t code = 1; // block size
        size_t code_idx = 0, dst_size = 1;
        for (size_t i = 0; i < src_size; ++i) {
            if (src[i]) {
                dst[dst_size++] = src[i];
                if (++code == 255) { goto restart; }
            } else {
            restart:
                dst[code_idx] = code;
                code = 1;
                code_idx = dst_size++;
            }
        }
        if (code <= dst[dst_size - 1]) {
            dst[code_idx] = dst[--dst_size];
        } else {
            dst[code_idx] = code;
        }
        return dst_size;
    }

    inline size_t decode(const uint8_t* src, size_t src_size, uint8_t* dst) {
        if (!src_size) { return 0; }

        size_t src_idx = 0, dst_size = 0;
        for (;;) {
            size_t remaining = src_size - src_idx;
            uint8_t code = src[src_idx++];
            if (code > remaining) {
                while (src_idx < src_size) { dst[dst_size++] = src[src_idx++]; }
                dst[dst_size++] = code;
                return dst_size;
            } else {
                for (uint8_t i = 1; i < code; ++i) { dst[dst_size++] = src[src_idx++]; }
                if (src_idx == src_size) { return dst_size; }
                if (code != 255) { dst[dst_size++] = 0; }
            }
        }
    }
}

#endif
