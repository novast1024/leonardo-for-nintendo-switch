def encode(data: bytes) -> bytes:
    """
    Encode data using Consistent Overhead Byte Stuffing / Reduced (COBS/R).
    Returns a bytes object with no zero bytes.
    """

    if not data:
        return b"\x01"

    # Allocate buffer: every 254 bytes may require an extra code byte
    buf = bytearray(len(data) + len(data) // 254 + 1)

    write_index = 1
    code_index = 0
    code = 1 # Distance to the next zero or block boundary

    for byte in data:
        if byte != 0:
            buf[write_index] = byte
            write_index += 1
            code += 1
            if code == 0xFF:
                # Finalize the current code (i.e. close the block) and start a new block
                buf[code_index] = code
                code_index = write_index
                write_index += 1
                code = 1
        else:
            # Finalize the current code (i.e. close the block) and start a new block
            buf[code_index] = code
            code_index = write_index
            write_index += 1
            code = 1

    # --- COBS/R optimization ---
    # If the last data byte is greater than or equal to the final code value,
    # it can replace the code byte directly, and the redundant last byte
    # can be removed from the sequence.
    if data[-1] >= code:
        buf[code_index] = data[-1]
        write_index -= 1
    else:
        buf[code_index] = code

    return bytes(buf[:write_index])

def decode(data: bytes) -> bytes:
    """
    Decode a byte sequence encoded with Consistent Overhead Byte Stuffing/Reduced (COBS/R).
    Return the decoded original byte sequence.
    """

    if not data:
        return b""

    if 0 in data:
        raise ValueError("COBS/R data must not contain zero bytes")

    result = bytearray()
    i = 0 # Index of the current code byte
    while True:
        code = data[i]
        if (code > len(data) - i):
            # The final block with 1-byte reduction
            result.extend(data[i+1:])
            result.append(code)
            break

        result.extend(data[i+1:i+code])
        i += code
        if i == len(data):
            # The current block is final (same as standard COBS)
            break
        if code != 0xFF:
            # Insert a zero before next block
            result.append(0x00)
    return bytes(result)

if __name__ == "__main__":
    print("< COBS/R Encode/Decode Tests >")

    data = b"\x2F\xA2\x00\x92\x73\x03"
    print(f"raw:     {data.hex(" ")}")
    data = encode(data)
    print(f"encoded: {data.hex(" ")}")
    data = decode(data)
    print(f"decoded: {data.hex(" ")}")

    print("="*30)

    data = b"\x2F\xA2\x00\x92\x73\x04"
    print(f"raw:     {data.hex(" ")}")
    data = encode(data)
    print(f"encoded: {data.hex(" ")}")
    data = decode(data)
    print(f"decoded: {data.hex(" ")}")

    print("="*30)

    import random
    for i in range(10000):
        raw = random.randbytes(random.randint(0, 1000))
        encoded = encode(raw)
        decoded = decode(encoded)
        if raw != decoded:
            raise Exception(f"ERR at attempt {i}")
    print("All tests passed!")