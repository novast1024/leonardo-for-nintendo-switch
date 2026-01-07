# https://protobuf.dev/programming-guides/encoding/

def encode(value: int) -> bytearray:
    """Encode a non-negative integer into Varint format."""
    if value < 0:
        raise ValueError("Negative integer is not supported.")

    result = bytearray()
    while value >= 0x80:
        result.append((value & 0x7f) | 0x80)
        value >>= 7
    result.append(value)
    return result

def decode(data: bytes) -> int:
    """Decode a Varint from the given byte sequence and return only the value."""
    return decode_with_length(data)[0]

def decode_with_length(data: bytes) -> tuple[int, int]:
    """Decode a Varint from the given byte sequence and return (value, consumed_bytes)."""
    offset = 0
    result = 0
    for consumed, byte in enumerate(data, start=1):
        result |= (byte & 0x7F) << offset
        if not (byte & 0x80):
            return result, consumed
        offset += 7
    raise ValueError("Invalid varint encoding: missing termination")