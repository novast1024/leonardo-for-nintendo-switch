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
# | Bytes |           3           |            4         |           5           |            6         |
# |-------+-----------------------+----------------------+-----------------------+----------------------|
# | L / R |                       L                      |                       R                      |
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
from typing import final, Self, Generator
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

    def __init__(self, x: float, y: float) -> None:
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def rotate(self, degrees: float) -> Self:
        if degrees % 360.0 == 0.0 or self == self.ZERO:
            return self
        rad = math.radians(degrees)
        cos = math.cos(rad)
        sin = math.sin(rad)
        return self.__class__(
            self._x * cos - self._y * sin,
            self._x * sin + self._y * cos
        )

    def __add__(self, other: Self) -> Self:
        if self == self.ZERO:
            return other
        if other == self.ZERO:
            return self
        return self.__class__(self._x + other._x, self._y + other._y)

    def __sub__(self, other: Self) -> Self:
        if other == self.ZERO:
            return self
        return self.__class__(self._x - other._x, self._y - other._y)

    def __mul__(self, value: float) -> Self:
        if value == 0.0:
            return self.ZERO
        return self.__class__(self._x * value, self._y * value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self._x == other._x and self._y == other._y

    def __iter__(self) -> Generator[float, None, None]:
        yield self._x
        yield self._y

    def __repr__(self) -> str:
        return f"Vector({self._x:0.1f}, {self._y:0.1f})"

    def clamp_magnitude(self, max_magnitude: float) -> Self:
        mag = math.sqrt(self._x * self._x + self._y * self._y)
        if mag <= max_magnitude:
            return self
        else:
            scale = max_magnitude / mag
            return self.__class__(self._x * scale, self._y * scale)

Vector.ZERO = Vector(0.0, 0.0)
Vector.UP = Vector(0.0, -1.0)
Vector.DOWN = Vector(0.0, 1.0)
Vector.LEFT = Vector(-1.0, 0.0)
Vector.RIGHT = Vector(1.0, 0.0)

# ==================================================================================================== #

@final
class BitFlags:
    NONE: Self = None # type: ignore

    @property
    def value(self):
        return self._value

    def __init__(self, value: int) -> None:
        self._value = value

    def __add__(self, other: Self) -> Self:
        if self._value == 0:
            return other
        if other._value == 0 or self._value == other._value:
            return self
        return self.__class__(self._value | other._value)

    def __sub__(self, other: Self) -> Self:
        if other._value == 0:
            return self
        elif self._value == other._value:
            return self.NONE
        return self.__class__(self._value & ~other._value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self._value == other._value

BitFlags.NONE = BitFlags(0)

# ==================================================================================================== #

#             direction UP   UP+RIGHT RIGHT DOWN+RIGHT DOWN DOWN+LEFT  LEFT  UP+LEFT
#             value     0       1       2       3       4       5       6       7       8
_hat_switch_table = (0b0001, 0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0000)

class GamepadState:
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
        lx, ly, rx, ry = map(
            lambda n: (n - 0x80) / 127.0 if n >= 0x80 else (n - 0x80) / 128.0,
            data[3:7]
        )

        return cls(
            BitFlags(int.from_bytes(data[0:2], "little")),
            BitFlags(_hat_switch_table[data[2] if data[2] <= 8 else 8]),
            Vector(lx, ly),
            Vector(rx, ry)
        )

    def __str__(self) -> str:
        return "+".join(itertools.chain(
            (name for i, name in enumerate(("Y","B","A","X","L","R","ZL","ZR","MINUS","PLUS","LS","RS","HOME","CAPTURE")) if self._buttons.value & (1 << i)),
            (name for i, name in enumerate(("UP", "DOWN", "LEFT", "RIGHT")) if self._hat_switch.value & (1 << i)),
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

class MacroNode:
    def __init__(self, state: GamepadState, duration: float) -> None:
        self._state = state
        self._duration = duration

    @property
    def state(self):
        return self._state

    @property
    def duration(self):
        return self._duration

    def __str__(self) -> str:
        return f"({self._state}, {self._duration})"

class MacroBuilder:
    def __init__(self):
        self._nodes: list[MacroNode] = []

    def hold(self, state: GamepadState, duration: float) -> Self:
        if not (0.0 <= duration):
            raise ValueError("hold time must be >= 0.0")

        if duration == 0.0:
            return self

        self._nodes.append(MacroNode(state, duration))
        return self

    def delay(self, seconds: float) -> Self:
        if not (0.0 <= seconds):
            raise ValueError("delay must be >= 0.0")

        if seconds == 0.0:
            return self

        self._nodes.append(MacroNode(NEUTRAL, seconds))
        return self

    def __iter__(self):
        node = None
        for next in [node for node in self._nodes if node.duration]:
            if node:
                if node.state == next.state:
                    node = MacroNode(node.state, node.duration + next.duration)
                else:
                    yield node
                    node = next
            else:
                node = next
        if node:
            yield node
            if node.state != NEUTRAL:
                yield MacroNode(NEUTRAL, 0.0)

# ==================================================================================================== #

if __name__ == "__main__":
    builder = MacroBuilder()

    for deg in range(0, 360, 15):
        builder.hold(LS(Vector.UP.rotate(deg)), 0.30)
    # (
    #     builder
    #     .hold(Button.A, 0.1)
    #     .hold(LS(Vector.UP), 5)
    # )
    from converter import encode
    # for data in builder:
    #     cmd = encode(data.state.__bytes__(), data.duration)

    z = b"".join(map(lambda data: encode(data.state.__bytes__(), data.duration), builder))
    print(len(z))
