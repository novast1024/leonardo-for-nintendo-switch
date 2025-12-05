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

from __future__ import annotations
from typing import final, Any, Self, Generator
import math
import itertools

# ==================================================================================================== #

@final
class Vector:
    ZERO: Self = None # type: ignore
    UP: Self = None # type: ignore
    DOWN: Self = None # type: ignore
    LEFT: Self = None # type: ignore
    RIGHT: Self = None # type: ignore

    x: float
    y: float

    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)

    def __setattr__(self, name: str, value: Any):
        raise AttributeError("read-only")

    def __delattr__(self, name: str) -> None:
        raise ArithmeticError("read-only")

    def __add__(self, other: Self) -> Self:
        if self.x == 0.0 and self.y == 0.0:
            return other
        if other.x == 0.0 and other.y == 0.0:
            return self
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        if other.x == 0.0 and other.y == 0.0:
            return self
        return self.__class__(self.x - other.x, self.y - other.y)

    def __mul__(self, value: float) -> Self:
        if value == 0.0:
            return self.ZERO
        return self.__class__(self.x * value, self.y * value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.x == other.x and self.y == other.y

    def __iter__(self) -> Generator[float, None, None]:
        yield self.x
        yield self.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Vector({self.x:0.1f}, {self.y:0.1f})"

    def rotate(self, degrees: float) -> Self:
        if (degrees % 360.0 == 0.0) or (self.x == 0.0 and self.y == 0.0):
            return self
        rad = math.radians(degrees)
        cos = math.cos(rad)
        sin = math.sin(rad)
        return self.__class__(
            self.x * cos - self.y * sin,
            self.x * sin + self.y * cos
        )

    def clamp_magnitude(self, max_magnitude: float) -> Self:
        mag = math.sqrt(self.x * self.x + self.y * self.y)
        if mag <= max_magnitude:
            return self
        else:
            scale = max_magnitude / mag
            return self.__class__(self.x * scale, self.y * scale)

Vector.ZERO = Vector(0.0, 0.0)
Vector.UP = Vector(0.0, -1.0)
Vector.DOWN = Vector(0.0, 1.0)
Vector.LEFT = Vector(-1.0, 0.0)
Vector.RIGHT = Vector(1.0, 0.0)

# ==================================================================================================== #

@final
class BitFlags:
    NONE: Self = None # type: ignore

    value: int

    __slots__ = ("value")

    def __init__(self, value: int) -> None:
        object.__setattr__(self, "value", value)

    def __setattr__(self, name: str, value: Any):
        raise AttributeError("read-only")

    def __delattr__(self, name: str) -> None:
        raise ArithmeticError("read-only")

    def __add__(self, other: Self) -> Self:
        if self.value == 0:
            return other
        if other.value == 0 or self.value == other.value:
            return self
        return self.__class__(self.value | other.value)

    def __sub__(self, other: Self) -> Self:
        if other.value == 0:
            return self
        elif self.value == other.value:
            return self.NONE
        return self.__class__(self.value & ~other.value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

BitFlags.NONE = BitFlags(0)

# ==================================================================================================== #

#             direction UP   UP+RIGHT RIGHT DOWN+RIGHT DOWN DOWN+LEFT  LEFT  UP+LEFT
#             value     0       1       2       3       4       5       6       7       8
_hat_switch_table = (0b0001, 0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0000)

_BUTTON_NAMES = [f"Button.{s}" for s in ("Y","B","A","X","L","R","ZL","ZR","MINUS","PLUS","LS","RS","HOME","CAPTURE")]
_HAT_NAMES = [f"Button.{s}" for s in ("UP", "DOWN", "LEFT", "RIGHT")]

class GamepadState:
    __slots__ = ("_buttons", "_hat_switch", "_left_stick", "_right_stick")

    def __init__(
        self,
        buttons: BitFlags = BitFlags.NONE,
        hat_switch: BitFlags = BitFlags.NONE,
        left_stick: Vector = Vector.ZERO,
        right_stick: Vector = Vector.ZERO
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
            Vector(lx, ly),
            Vector(rx, ry)
        )

    def __str__(self) -> str:
        return "+".join(itertools.chain(
            (name for i, name in enumerate(_BUTTON_NAMES) if self._buttons.value & (1 << i)),
            (name for i, name in enumerate(_HAT_NAMES) if self._hat_switch.value & (1 << i)),
            () if self._left_stick == Vector.ZERO else (f"LS({self._left_stick})",),
            () if self._right_stick == Vector.ZERO else (f"LS({self._right_stick})",)
        )) or "NEUTRAL"

NEUTRAL = GamepadState()

class Button:
    Y = GamepadState(buttons = BitFlags(0x01))
    B = GamepadState(buttons = BitFlags(0x02))
    A = GamepadState(buttons = BitFlags(0x04))
    X = GamepadState(buttons = BitFlags(0x08))
    L = GamepadState(buttons = BitFlags(0x10))
    R = GamepadState(buttons = BitFlags(0x20))
    ZL = GamepadState(buttons = BitFlags(0x40))
    ZR = GamepadState(buttons = BitFlags(0x80))
    MINUS = GamepadState(buttons = BitFlags(0x0100))
    PLUS = GamepadState(buttons = BitFlags(0x0200))
    LS = GamepadState(buttons = BitFlags(0x0400))
    RS = GamepadState(buttons = BitFlags(0x0800))
    HOME = GamepadState(buttons = BitFlags(0x1000))
    CAPTURE = GamepadState(buttons = BitFlags(0x2000))

    UP = GamepadState(hat_switch = BitFlags(0x01))
    DOWN = GamepadState(hat_switch = BitFlags(0x02))
    LEFT = GamepadState(hat_switch = BitFlags(0x04))
    RIGHT = GamepadState(hat_switch = BitFlags(0x08))


def LS(vector: Vector) -> GamepadState:
    return GamepadState(left_stick=vector)

def RS(vector: Vector) -> GamepadState:
    return GamepadState(right_stick=vector)

# ==================================================================================================== #
