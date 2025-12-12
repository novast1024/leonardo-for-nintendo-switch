from typing import Generator, NamedTuple, Iterable, Self
import itertools

from models.gamepad import Gamepad, NEUTRAL
from protocols import varint

class InputData(NamedTuple):
    state: Gamepad
    duration: float

    def __str__(self) -> str:
        return f"({self.state}, {self.duration})"

class MacroBuilder:
    def __init__(self):
        self._nodes: list[InputData] = []

    def hold(self, state: Gamepad, duration: float) -> Self:
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

# complex report, basic report, loop start, loop end,


LOOP_START_OPCODE = b"\x0e"
LOOP_END_OPCODE = b"\x0f"

basic_opcode_map = {
    b"\x00\x00\x08\x80\x80\x80\x80": b"\x10",

    b"\x01\x00\x08\x80\x80\x80\x80": b"\x11",
    b"\x02\x00\x08\x80\x80\x80\x80": b"\x12",
    b"\x04\x00\x08\x80\x80\x80\x80": b"\x13",
    b"\x08\x00\x08\x80\x80\x80\x80": b"\x14",
    b"\x10\x00\x08\x80\x80\x80\x80": b"\x15",
    b"\x20\x00\x08\x80\x80\x80\x80": b"\x16",
    b"\x40\x00\x08\x80\x80\x80\x80": b"\x17",
    b"\x80\x00\x08\x80\x80\x80\x80": b"\x18",
    b"\x00\x01\x08\x80\x80\x80\x80": b"\x19",
    b"\x00\x02\x08\x80\x80\x80\x80": b"\x1a",
    b"\x00\x04\x08\x80\x80\x80\x80": b"\x1b",
    b"\x00\x08\x08\x80\x80\x80\x80": b"\x1c",
    b"\x00\x10\x08\x80\x80\x80\x80": b"\x1d",
    b"\x00\x20\x08\x80\x80\x80\x80": b"\x1e",

    b"\x00\x00\x00\x80\x80\x80\x80": b"\x1f",
    b"\x00\x00\x01\x80\x80\x80\x80": b"\x20",
    b"\x00\x00\x02\x80\x80\x80\x80": b"\x21",
    b"\x00\x00\x03\x80\x80\x80\x80": b"\x22",
    b"\x00\x00\x04\x80\x80\x80\x80": b"\x23",
    b"\x00\x00\x05\x80\x80\x80\x80": b"\x24",
    b"\x00\x00\x06\x80\x80\x80\x80": b"\x25",
    b"\x00\x00\x07\x80\x80\x80\x80": b"\x26",

    b"\x00\x00\x08\x80\x00\x80\x80": b"\x27",
    b"\x00\x00\x08\xda\x25\x80\x80": b"\x28",
    b"\x00\x00\x08\xff\x80\x80\x80": b"\x29",
    b"\x00\x00\x08\xda\xda\x80\x80": b"\x2a",
    b"\x00\x00\x08\x80\xff\x80\x80": b"\x2b",
    b"\x00\x00\x08\x25\xda\x80\x80": b"\x2c",
    b"\x00\x00\x08\x00\x80\x80\x80": b"\x2d",
    b"\x00\x00\x08\x25\x25\x80\x80": b"\x2e",

    b"\x00\x00\x08\x80\x80\x80\x00": b"\x2f",
    b"\x00\x00\x08\x80\x80\xda\x25": b"\x30",
    b"\x00\x00\x08\x80\x80\xff\x80": b"\x31",
    b"\x00\x00\x08\x80\x80\xda\xda": b"\x32",
    b"\x00\x00\x08\x80\x80\x80\xff": b"\x33",
    b"\x00\x00\x08\x80\x80\x25\xda": b"\x34",
    b"\x00\x00\x08\x80\x80\x00\x80": b"\x35",
    b"\x00\x00\x08\x80\x80\x25\x25": b"\x36",
}

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
def encode_instruction(data: InputData) -> bytes:
    ms = round(data.duration * 1000)

    if not (ms <= UINT32_MAX):
        raise ValueError(f"Exceeded maximum threashold: {UINT32_MAX}, received {ms}")

    opcode = basic_opcode_map.get(data.state.__bytes__(), None)
    if opcode is not None:
        return bytes(itertools.chain(opcode, bytes(varint.encode(ms))))
    else:
        opcode = 0x80
        diff = bytearray()
        for i, byte in enumerate(data.state.__bytes__()):
            if byte != NEUTRAL_BYTES[i]:
                opcode |= i << i
                diff.append(byte)

        opcode.to_bytes()
        return bytes(itertools.chain((opcode,), diff, varint.encode(ms)))

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
                result.append(LOOP_START_OPCODE + bytes(varint.encode(count)))
                result.extend(segment)
                result.append(LOOP_END_OPCODE)
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


# ==================================================================================================== #



# if __name__ == "__main__":

#     builder = MacroBuilder()

#     # for deg in range(0, 360, 15):
#     #     builder.hold(LS(Vec2.UP.rotate(deg)), 0.30)

#     press_time = 0.05
#     press_interval = 0.05
#     builder.hold(Button.A, press_time).delay(press_interval)
#     for i in range(2):
#         builder.hold(LS(Vec2.DOWN), press_time).delay(press_interval)
#     for i in range(3):
#         builder.hold(LS(Vec2.RIGHT), press_time).delay(press_interval)



#     z = compress_repetition(list(map(lambda node: encode_input_command(node), clean(builder))))
#     print(len(z))