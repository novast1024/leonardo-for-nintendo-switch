#ifndef CRC8_H
#define CRC8_H

// https://www.3dbrew.org/wiki/CRC-8-CCITT
#include <stdint.h>
#include <string.h>

uint8_t crc8ccitt(const void * data, size_t size);

#endif