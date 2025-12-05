from typing import Generator, NamedTuple, Iterable, Self
import itertools

from hori_gamepad import GamepadState, NEUTRAL, Button, Vector, LS, RS
import varint

class InputData(NamedTuple):
    state: GamepadState
    duration: float

    def __str__(self) -> str:
        return f"({self.state}, {self.duration})"

class MacroBuilder:
    def __init__(self):
        self._nodes: list[InputData] = []

    def hold(self, state: GamepadState, duration: float) -> Self:
        if not (0.0 <= duration):
            raise ValueError("hold time must be >= 0.0")

        if duration == 0.0:
            return self

        self._nodes.append(InputData(state, duration))
        return self

    def delay(self, seconds: float) -> Self:
        if not (0.0 <= seconds):
            raise ValueError("delay must be >= 0.0")

        if seconds == 0.0:
            return self

        self._nodes.append(InputData(NEUTRAL, seconds))
        return self

    def __iter__(self):
        yield from self._nodes

def clean(data: Iterable[InputData]):
    crnt = None
    for next in [e for e in data if e.duration]:
        if crnt:
            if crnt.state == next.state:
                crnt = InputData(crnt.state, crnt.duration + next.duration)
            else:
                yield crnt
                crnt = next
        else:
            crnt = next
    if crnt:
        yield crnt
        if crnt.state != NEUTRAL:
            yield InputData(NEUTRAL, 0.0)

# ==================================================================================================== #

basic_input_code = {
    NEUTRAL: 0x00,
    Button.Y: 0x01,
    Button.B: 0x02,
    Button.A: 0x03,
    Button.X: 0x04,
    Button.L: 0x05,
    Button.R: 0x06,
    Button.ZL: 0x07,
    Button.ZR: 0x08,
    Button.MINUS: 0x09,
    Button.PLUS: 0x0a,
    Button.LS: 0x0b,
    Button.RS: 0x0c,
    Button.HOME: 0x0d,
    Button.CAPTURE: 0x0e,

    Button.UP: 0x0f,
    Button.RIGHT: 0x11,
    Button.DOWN: 0x12,
    Button.LEFT: 0x13,

    LS(Vector.UP): 0x14,
    LS(Vector.RIGHT): 0x15,
    LS(Vector.DOWN): 0x16,
    LS(Vector.LEFT): 0x17,

    RS(Vector.UP): 0x18,
    RS(Vector.RIGHT): 0x19,
    RS(Vector.DOWN): 0x1a,
    RS(Vector.LEFT): 0x1b,
}

LOOP_START_CODE = b"\x1e"
LOOP_END_CODE = b"\x1f"

UINT32_MAX = 0xFFFFFFFF

# raise ValueError("Value exceeds Arduino Leonardo unsigned long (uint32_t) limit.")


NEUTRAL_BYTES = bytes(NEUTRAL)


# basic input command
# +-------------------------------+-----------+
# |            command            | parameter |
# +---+---+---+---+---+---+---+---+-----------+
# | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | 1-5 bytes |
# |---+---+---+---+---+---+---+---+  Duration |
# | 0 |         code              |  (Varint) |
# +---+-------+-------------------+-----------+

# complex input command
# +---------------------------------------------------+------------+
# |        command (length = popcnt(FIRST_BYTE))      |  parameter |
# +---+----+----+----+----+-----+----+----+-----------+------------+
# | 7 |  6 |  5 |  4 |  3 |  2  |  1 |  0 | 0-7 bytes | 1-5 bytes  |
# |---+----+----+----+----+-----+----+----| Diff from |  Duration  |
# | 1 | Rx | Ry | Lx | Ly | Hat | B1 | B0 | NEUTRAL   |  (Varint)  |
# +---+----+----+----+----+-----+----+----+-----------+------------+

# loop start command
# +-------------------------------+-----------+
# |            command            | parameter |
# +---+---+---+---+---+---+---+---+-----------+
# | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | 1-5 bytes |
# |---+---+---+---+---+---+---+---+ LoopCount |
# | 0 |         code              |  (Varint) |
# +---+-------+-------------------+-----------+

# loop end command
# +-------------------------------+
# |            command            |
# +---+---+---+---+---+---+---+---+
# | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
# |---+---+---+---+---+---+---+---+
# | 0 |         code              |
# +---+-------+-------------------+
def encode_input_command(data: InputData) -> bytes:
    ms = round(data.duration * 1000)

    if not (ms <= UINT32_MAX):
        raise ValueError(f"Exceeded maximum threashold: {UINT32_MAX}, received {ms}")

    code = basic_input_code.get(data.state, None)
    if code is not None:
        return bytes(itertools.chain((code,), bytes(varint.encode(ms))))
    else:
        code = 0x80
        diff = bytearray()
        for i, byte in enumerate(data.state.__bytes__()):
            if byte != NEUTRAL_BYTES[i]:
                code |= i << i
                diff.append(byte)

        code.to_bytes()
        return bytes(itertools.chain((code,), diff, varint.encode(ms)))

def compress_repetition(data: list[bytes], min_len: int = 1):
    result: list[bytes] = []
    i = 0
    while i < len(data):
        found = False
        for length in range(min_len, len(data) // 2+1):
            segment = data[i:i+length]
            count = 0
            j = i
            while data[j:j+length] == segment:
                count += 1
                j += length
            if count > 1:
                result.append(LOOP_START_CODE + bytes(varint.encode(count)))
                result.extend(segment)
                result.append(LOOP_END_CODE)
                i = j
                found = True
                break
        if not found:
            result.append(data[i])
            i += 1
    return b"".join(result)


# ==================================================================================================== #

# ==================================================================================================== #

def split_bytes(data: bytes, chunk_size: int) -> Generator[bytes, None, None]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    return (data[i:i+chunk_size] for i in range(0, len(data), chunk_size))

# ==================================================================================================== #

# ==================================================================================================== #

def cobsr_encode(src: bytes) -> bytes:
    if not src:
        return b"\x01"

    dst = bytearray(len(src) + len(src) // 254 + 1)
    code = 1
    code_idx = 0
    dst_size = 1
    for byte in src:
        if byte:
            dst[dst_size] = byte
            dst_size += 1
            code += 1
        if not byte or code == 0xff:
            dst[code_idx] = code
            code = 1
            code_idx = dst_size
            dst_size += 1
    if code < src[-1]:
        dst[code_idx] = src[-1]
        dst_size -= 1
    else:
        dst[code_idx] = code
    return bytes(dst[:dst_size])

def test(raw: bytes):
    enc = cobsr_encode(raw)
    print("raw    :", raw.hex(" "))
    print("encoded:", enc.hex(" "))

# test(b'\x00\x11"\x003D\x00')
# ==================================================================================================== #



# if __name__ == "__main__":

#     builder = MacroBuilder()

#     # for deg in range(0, 360, 15):
#     #     builder.hold(LS(Vector.UP.rotate(deg)), 0.30)

#     press_time = 0.05
#     press_interval = 0.05
#     builder.hold(Button.A, press_time).delay(press_interval)
#     for i in range(2):
#         builder.hold(LS(Vector.DOWN), press_time).delay(press_interval)
#     for i in range(3):
#         builder.hold(LS(Vector.RIGHT), press_time).delay(press_interval)



#     z = compress_repetition(list(map(lambda node: encode_input_command(node), clean(builder))))
#     print(len(z))