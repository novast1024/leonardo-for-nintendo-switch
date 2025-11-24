from typing import Generator

# update event: header MSB == 0
# header 7 bit flags + delta_time (varint) + delta_bytes (0-7 bytes)

# MSB == 1
# header loop_count (varint) +
# 0b1000_0000



code_map = {
    b"\x00\x00\x08\x80\x80\x80\x80": 0x00, # neutral
    b"\x01\x00\x08\x80\x80\x80\x80": 0x01, # Button.Y
    b"\x02\x00\x08\x80\x80\x80\x80": 0x02, # Button.B
    b"\x04\x00\x08\x80\x80\x80\x80": 0x03, # Button.A
    b"\x08\x00\x08\x80\x80\x80\x80": 0x04, # Button.X
    b"\x10\x00\x08\x80\x80\x80\x80": 0x05, # Button.L
    b"\x20\x00\x08\x80\x80\x80\x80": 0x06, # Button.R
    b"\x40\x00\x08\x80\x80\x80\x80": 0x07, # Button.ZL
    b"\x80\x00\x08\x80\x80\x80\x80": 0x08, # Button.ZR
    b"\x00\x01\x08\x80\x80\x80\x80": 0x09, # Button.MINUS
    b"\x00\x02\x08\x80\x80\x80\x80": 0x0a, # Button.PLUS
    b"\x00\x04\x08\x80\x80\x80\x80": 0x0b, # Button.LS
    b"\x00\x08\x08\x80\x80\x80\x80": 0x0c, # Button.RS
    b"\x00\x10\x08\x80\x80\x80\x80": 0x0d, # Button.HOME
    b"\x00\x20\x08\x80\x80\x80\x80": 0x0e, # Button.CAPTURE

    b"\x00\x00\x00\x80\x80\x80\x80": 0x0f, # Button.UP
    b"\x00\x00\x02\x80\x80\x80\x80": 0x11, # Button.RIGHT
    b"\x00\x00\x04\x80\x80\x80\x80": 0x12, # Button.DOWN
    b"\x00\x00\x06\x80\x80\x80\x80": 0x13, # Button.LEFT

    b"\x00\x00\x08\x80\x00\x80\x80": 0x14, # LS(Vector.UP)
    b"\x00\x00\x08\xff\x80\x80\x80": 0x15, # LS(Vector.RIGHT)
    b"\x00\x00\x08\x80\xff\x80\x80": 0x16, # LS(Vector.DOWN)
    b"\x00\x00\x08\x00\x80\x80\x80": 0x17, # LS(Vector.LEFT)

    b"\x00\x00\x08\x80\x80\x80\x00": 0x18, # RS(Vector.UP)
    b"\x00\x00\x08\x80\x80\xff\x80": 0x19, # RS(Vector.RIGHT)
    b"\x00\x00\x08\x80\x80\x80\xff": 0x1a, # RS(Vector.DOWN)
    b"\x00\x00\x08\x80\x80\x00\x80": 0x1b, # RS(Vector.LEFT)
}

LOOP_START = 0x1c
LOOP_END = 0x1e

# +-------------------------------+-----------+
# |           1 Byte              | 0-4 Bytes |
# +---+---+---+---+---+---+---+---+-----------+
# | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |           |
# |---+---+---+---+---+---+---+---+   number  |
# | 0 |  size |       code        |           |
# +---+-------+-------------------+-----------+
# size (number size)         if code is LOOP_START or LOOP_END:
# 00 => 0 byte                   number is loop_count
# 01 => 1 bytes              else:
# 10 => 2 bytes                  number is delta_time
# 11 => 4 bytes


# MSB=1
# +---------------------------------------+-------------+------------+
# |               1 Byte                  |  0-7 Bytes  |  1-4 Bytes |
# +---+----+----+----+----+-----+----+----+-------------+------------+
# | 7 |  6 |  5 |  4 |  3 |  2  |  1 |  0 |             |  Duration  |
# |---+----+----+----+----+-----+----+----| Delta Bytes | Delta Time |
# | 1 | Rx | Ry | Lx | Ly | Hat | B1 | B0 |             |  (Varint)  |
# +---+----+----+----+----+-----+----+----+-------------+------------+
#

# "Y","B","A","X","L","R","ZL","ZR","Minus","Plus","LS","RS","Home","Capture"  14
# Up, Up+Right, Right, Down+Right, Down, Down+Left, Left, Up+Left 8

b"\x00\x00\x08\x80\x80\x80\x80"

# ============================================================================

# Varint (unsigned integer)
# +------------------+---+---+---+---+---+---+---+
# |        7         | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
# |------------------|---+---+---+---+---+---+---+
# | continuation bit |       payload bits        |
# +------------------+---------------------------+
# e.g. 40 => 0b0010_1000
#     100 => 0b0110_0100
#    1000 => 0b1110_1000 0b0000_0111
def encode_varint(value: int) -> list[int]:
    if value < 0:
        raise ValueError("Negative integer is not supported.")

    result: list[int] = []
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            result.append(byte | 0x80)
        else:
            result.append(byte)
            break
    return result

def decode_varint(data: bytes) -> tuple[int, int]:
    offset = 0
    result = 0
    for size, byte in enumerate(data, start=1):
        result |= (byte & 0x7F) << offset
        if not (byte & 0x80):
            return result, size
        offset += 7
    raise ValueError("Invalid varint encoding")

# ============================================================================

def split_bytes(data: bytes, chunk_size: int) -> Generator[bytes, None, None]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    return (data[i:i+chunk_size] for i in range(0, len(data), chunk_size))

# ============================================================================

CRC8_CCITT_TABLE = (
    b"\x00\x07\x0E\x09\x1C\x1B\x12\x15\x38\x3F\x36\x31\x24\x23\x2A\x2D"
    b"\x70\x77\x7E\x79\x6C\x6B\x62\x65\x48\x4F\x46\x41\x54\x53\x5A\x5D"
    b"\xE0\xE7\xEE\xE9\xFC\xFB\xF2\xF5\xD8\xDF\xD6\xD1\xC4\xC3\xCA\xCD"
    b"\x90\x97\x9E\x99\x8C\x8B\x82\x85\xA8\xAF\xA6\xA1\xB4\xB3\xBA\xBD"
    b"\xC7\xC0\xC9\xCE\xDB\xDC\xD5\xD2\xFF\xF8\xF1\xF6\xE3\xE4\xED\xEA"
    b"\xB7\xB0\xB9\xBE\xAB\xAC\xA5\xA2\x8F\x88\x81\x86\x93\x94\x9D\x9A"
    b"\x27\x20\x29\x2E\x3B\x3C\x35\x32\x1F\x18\x11\x16\x03\x04\x0D\x0A"
    b"\x57\x50\x59\x5E\x4B\x4C\x45\x42\x6F\x68\x61\x66\x73\x74\x7D\x7A"
    b"\x89\x8E\x87\x80\x95\x92\x9B\x9C\xB1\xB6\xBF\xB8\xAD\xAA\xA3\xA4"
    b"\xF9\xFE\xF7\xF0\xE5\xE2\xEB\xEC\xC1\xC6\xCF\xC8\xDD\xDA\xD3\xD4"
    b"\x69\x6E\x67\x60\x75\x72\x7B\x7C\x51\x56\x5F\x58\x4D\x4A\x43\x44"
    b"\x19\x1E\x17\x10\x05\x02\x0B\x0C\x21\x26\x2F\x28\x3D\x3A\x33\x34"
    b"\x4E\x49\x40\x47\x52\x55\x5C\x5B\x76\x71\x78\x7F\x6A\x6D\x64\x63"
    b"\x3E\x39\x30\x37\x22\x25\x2C\x2B\x06\x01\x08\x0F\x1A\x1D\x14\x13"
    b"\xAE\xA9\xA0\xA7\xB2\xB5\xBC\xBB\x96\x91\x98\x9F\x8A\x8D\x84\x83"
    b"\xDE\xD9\xD0\xD7\xC2\xC5\xCC\xCB\xE6\xE1\xE8\xEF\xFA\xFD\xF4\xF3"
)

def crc8ccitt(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc = CRC8_CCITT_TABLE[crc ^ byte]
    return crc

# ============================================================================

def cobsr_encode(src: bytes) -> bytes:
    dst = bytearray(len(src) + len(src) // 254 + 1)
    code = 1
    code_idx = 0
    dst_size = 1
    for byte in src:
        if byte:
            dst[dst_size] = byte
            dst_size += 1
            code += 1
            if code == 255:
                dst[code_idx] = code
                code = 1
                code_idx = dst_size
                dst_size += 1
        else:
            dst[code_idx] = code
            code = 1
            code_idx = dst_size
            dst_size += 1
    if code != 1 and code < dst[dst_size - 1]:
        dst_size -= 1
        dst[code_idx] = dst[dst_size]
    else:
        dst[code_idx] = code
    return dst[0:dst_size]

def pack(src: bytes) -> bytes:
    return cobsr_encode(src + crc8ccitt(src).to_bytes())