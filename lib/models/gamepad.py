from typing import Self, final
import itertools

from .bitflags import BitFlags
from .vector import Vec2

# Horipad for Nintendo Switch Report (size: 8 Bytes)

# Buttons Bytes
# +-------+---------------------------------+-------------------------------------------------+
# | Bytes |             0                   |                     1                           |
# |-------|---+---+---+---+---+---+----+----|-------+------+----+----+------+---------+---+---|
# |  Bits | 0 | 1 | 2 | 3 | 4 | 5 |  6 |  7 |   0   |   1  |  2 |  3 |   4  |    5    | 6 | 7 |
# |-------|---|---|---|---|---|---|----|----|-------|------|----|----|------|---------|---|---|
# | Names | Y | B | A | X | L | R | ZL | ZR | MINUS | PLUS | LS | RS | HOME | CAPTURE | - | - |
# +-------+---+---+---+---+---+---+----+----+-------+------+----+----+------+---------+---+---+

# Hat Switch Byte
# +-------+---------------------------------------------------------------------------------+
# | Bytes |                                       2                                         |
# +-------+----+----------+-------+------------+------+-----------+------+---------+--------|
# | Values|  0 |     1    |   2   |     3      |   4  |     5     |   6  |    7    | x >= 8 |
# |-------|----|----------|-------|------------|------|-----------|------|---------|--------|
# | Names | UP | UP+RIGHT | RIGHT | DOWN+RIGHT | DOWN | DOWN+LEFT | LEFT | UP+LEFT | CENTER |
# +-------+----+----------+-------+------------+------+-----------+------+---------+--------+

# L & R Stick Bytes
# +-------+-----------------------+----------------------+-----------------------+----------------------+
# | Bytes |           3           |           4          |           5           |           6          |
# |-------+-----------------------+----------------------+-----------------------+----------------------|
# | L / R |         L(x)          |         L(y)         |         R(x)          |         R(y)         |
# |-------+------+--------+-------+------+--------+------+------+--------+-------+------+--------+------|
# | Bounds| 0x00 |  0x80  |  0xff | 0x00 |  0x80  | 0xff | 0x00 |  0x80  |  0xff | 0x00 |  0x80  | 0xff |
# |-------|------|--------|-------|------|--------|------|------|--------|-------|------|--------|------|
# | Names | LEFT | CENTER | RIGHT |  UP  | CENTER | DOWN | LEFT | CENTER | RIGHT |  UP  | CENTER | DOWN |
# +-------+------+--------+-------+------+--------+------+------+--------+-------+------+--------+------+

# Vendor-Specific Byte
# +-------+------+
# | Bytes |   7  |
# |-------|------|
# | Values| 0x00 |
# +-------+------+

#             direction UP   UP+RIGHT RIGHT DOWN+RIGHT DOWN DOWN+LEFT  LEFT  UP+LEFT
#             value     0       1       2       3       4       5       6       7       8
_hat_switch_table = (0b0001, 0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0000)

_BUTTON_NAMES = [f"Button.{s}" for s in ("Y","B","A","X","L","R","ZL","ZR","MINUS","PLUS","LS","RS","HOME","CAPTURE")]
_HAT_NAMES = [f"Button.{s}" for s in ("UP", "DOWN", "LEFT", "RIGHT")]

@final
class Gamepad:
    __slots__ = ("_buttons", "_hat_switch", "_left_stick", "_right_stick")

    def __init__(
        self,
        buttons: BitFlags = BitFlags.NONE,
        hat_switch: BitFlags = BitFlags.NONE,
        left_stick: Vec2 = Vec2.ZERO,
        right_stick: Vec2 = Vec2.ZERO
    ) -> None:
        self._buttons = buttons
        self._hat_switch = hat_switch
        self._left_stick = left_stick
        self._right_stick = right_stick

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and\
            self._buttons == other._buttons and\
            self._hat_switch == other._hat_switch and\
            self._left_stick == other._left_stick and\
            self._right_stick == other._right_stick

    def __hash__(self) -> int:
        return hash((self._buttons, self._hat_switch, self._left_stick, self._right_stick))

    def __add__(self, other: Self) -> Self:
        return self.__class__(
            self._buttons.__add__(other._buttons),
            self._hat_switch.__add__(other._hat_switch),
            self._left_stick.__add__(other._left_stick),
            self._right_stick.__add__(other._right_stick)
        )

    def __sub__(self, other: Self) -> Self:
        return self.__class__(
            self._buttons.__sub__(other._buttons),
            self._hat_switch.__sub__(other._hat_switch),
            self._left_stick.__sub__(other._left_stick),
            self._right_stick.__sub__(other._right_stick)
        )

    def __bytes__(self) -> bytes:
        btns0 = self._buttons.value & 0x00ff
        btns1 = (self._buttons.value & 0xff00) >> 8

        hat = self._hat_switch.value
        if hat & 0b1100 == 0b1100:
            hat &= 0b0011
        if hat & 0b0011 == 0b0011:
            hat &= 0b1100
        hat = _hat_switch_table.index(hat)

        lx, ly, rx, ry = map(
            lambda x: round(x * 127.0 + 128.0 if x >= 0.0 else x * 128.0 + 128.0),
            itertools.chain(
                self._left_stick.clamp_magnitude(1.0),
                self._right_stick.clamp_magnitude(1.0)
            )
        )

        return bytes((btns0, btns1, hat, lx, ly, rx, ry))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        btn = int.from_bytes(data[0:2], "little")
        hat = _hat_switch_table[data[2] if data[2] <= 8 else 8]

        lx, ly, rx, ry = map(
            lambda n: (n - 0x80) / 127.0 if n >= 0x80 else (n - 0x80) / 128.0,
            data[3:7]
        )

        return cls(
            BitFlags(btn),
            BitFlags(hat),
            Vec2(lx, ly),
            Vec2(rx, ry)
        )

    def __str__(self) -> str:
        return "+".join(itertools.chain(
            (name for i, name in enumerate(_BUTTON_NAMES) if self._buttons.value & (1 << i)),
            (name for i, name in enumerate(_HAT_NAMES) if self._hat_switch.value & (1 << i)),
            () if self._left_stick == Vec2.ZERO else (f"LS({self._left_stick})",),
            () if self._right_stick == Vec2.ZERO else (f"LS({self._right_stick})",)
        )) or "NEUTRAL"

NEUTRAL = Gamepad()

class Button:
    Y = Gamepad(buttons = BitFlags(0x01))
    B = Gamepad(buttons = BitFlags(0x02))
    A = Gamepad(buttons = BitFlags(0x04))
    X = Gamepad(buttons = BitFlags(0x08))
    L = Gamepad(buttons = BitFlags(0x10))
    R = Gamepad(buttons = BitFlags(0x20))
    ZL = Gamepad(buttons = BitFlags(0x40))
    ZR = Gamepad(buttons = BitFlags(0x80))
    MINUS = Gamepad(buttons = BitFlags(0x0100))
    PLUS = Gamepad(buttons = BitFlags(0x0200))
    LS = Gamepad(buttons = BitFlags(0x0400))
    RS = Gamepad(buttons = BitFlags(0x0800))
    HOME = Gamepad(buttons = BitFlags(0x1000))
    CAPTURE = Gamepad(buttons = BitFlags(0x2000))

    UP = Gamepad(hat_switch = BitFlags(0x01))
    DOWN = Gamepad(hat_switch = BitFlags(0x02))
    LEFT = Gamepad(hat_switch = BitFlags(0x04))
    RIGHT = Gamepad(hat_switch = BitFlags(0x08))

def LS(vector: Vec2) -> Gamepad:
    return Gamepad(left_stick=vector)

def RS(vector: Vec2) -> Gamepad:
    return Gamepad(right_stick=vector)