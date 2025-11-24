# Horipad for Nintendo Switch Report (size: 8 Bytes)

# Buttons Bytes
# +-------+---------------------------------+-------------------------------------------------+
# | Bytes |             0                   |                     1                           |
# |-------|---+---+---+---+---+---+----+----|-------+------+----+----+------+---------+---+---|
# |  Bits | 0 | 1 | 2 | 3 | 4 | 5 |  6 |  7 |   0   |   1  |  2 |  3 |   4  |    5    | 6 | 7 |
# |-------|---|---|---|---|---|---|----|----|-------|------|----|----|------|---------|---|---|
# | Names | Y | B | A | X | L | R | ZL | ZR | Minus | Plus | LS | RS | Home | Capture | - | - |
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
from typing import final, Self, Generator, Protocol
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

    def __init__(self, value: int) -> None:
        self.value = value

    def __add__(self, other: Self) -> Self:
        if self.value == 0:
            return other
        if other.value == 0 or self.value == other.value:
            return self
        return self.__class__(self.value | other.value)

    def __sub__(self, other: Self) -> Self:
        if other.value == 0:
            return self
        return self.__class__(self.value & ~other.value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value

BitFlags.NONE = BitFlags(0)

# ==================================================================================================== #

#             direction UP   UP+RIGHT RIGHT DOWN+RIGHT DOWN DOWN+LEFT  LEFT  UP+LEFT
#             value     0       1       2       3       4       5       6       7       8
_hat_switch_table = (0b0001, 0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0000)

class HoripadReport:
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
        import itertools
        return "+".join(itertools.chain(
            (name for i, name in enumerate(("Y","B","A","X","L","R","ZL","ZR","Minus","Plus","LS","RS","Home","Capture")) if self._buttons.value & (1 << i)),
            (name for i, name in enumerate(("UP", "DOWN", "LEFT", "RIGHT")) if self._hat_switch.value & (1 << i))
        ))

# ==================================================================================================== #

class Button:
    Y = HoripadReport(buttons = BitFlags(0x01))
    B = HoripadReport(buttons = BitFlags(0x02))
    A = HoripadReport(buttons = BitFlags(0x04))
    X = HoripadReport(buttons = BitFlags(0x08))
    L = HoripadReport(buttons = BitFlags(0x10))
    R = HoripadReport(buttons = BitFlags(0x20))
    ZL = HoripadReport(buttons = BitFlags(0x40))
    ZR = HoripadReport(buttons = BitFlags(0x80))
    MINUS = HoripadReport(buttons = BitFlags(0x0100))
    PLUS = HoripadReport(buttons = BitFlags(0x0200))
    LS = HoripadReport(buttons = BitFlags(0x0400))
    RS = HoripadReport(buttons = BitFlags(0x0800))
    HOME = HoripadReport(buttons = BitFlags(0x1000))
    CAPTURE = HoripadReport(buttons = BitFlags(0x2000))

    UP = HoripadReport(hat_switch = BitFlags(0x01))
    DOWN = HoripadReport(hat_switch = BitFlags(0x02))
    LEFT = HoripadReport(hat_switch = BitFlags(0x04))
    RIGHT = HoripadReport(hat_switch = BitFlags(0x08))


def LS(vector: Vector) -> HoripadReport:
    return HoripadReport(left_stick=vector)

def RS(vector: Vector) -> HoripadReport:
    return HoripadReport(right_stick=vector)


# ==================================================================================================== #

NUTRAL_REPORT = HoripadReport()

# ==================================================================================================== #

class Command(Protocol):
    def __bytes__(self) -> bytes: ...

class InputCommand:
    def __init__(self, data: HoripadReport, duration: float) -> None:
        self.data = data
        self.duration = duration

    def __bytes__(self) -> bytes:
        raise NotImplementedError("TODO: implement this function")

class LoopStartCommand:
    def __init__(self, times_to_repeat: int) -> None:
        self.times_to_repeat = times_to_repeat

    def __bytes__(self) -> bytes:
        raise NotImplementedError("TODO: implement this function")

class LoopEndCommand:
    def __bytes__(self) -> bytes:
        raise NotImplementedError("TODO: implement this function")


loop_depth = 0

MAX_LOOP_DEPTH = 5

class TooDeepLoopException(Exception):
    """Raised when the loop nesting depth exceeds MAX_LOOP_DEPTH."""
    pass

class UnclosedLoopError(Exception):
    """Raised when loop is not properly closed in the builder."""
    pass

class MacroBuilder:
    def init(
        self
    ):
        self.commands: list[Command] = []
        self.loop_depth = 0

    def loop(self, times_to_repeat: int) -> Self:
        if 0 < times_to_repeat:
            raise ValueError("times_to_repeat must be greater than 0")

        self.loop_depth += 1
        if loop_depth > MAX_LOOP_DEPTH:
            raise TooDeepLoopException(f"The loop depth is too high (current: {loop_depth}, allowed: {MAX_LOOP_DEPTH})")
        self.commands.append(LoopStartCommand(times_to_repeat))
        return self

    def end_loop(self) -> Self:
        self.loop_depth -= 1
        return self

    def hold(self, data: HoripadReport, duration: float) -> Self:
        if self.commands:
            self.commands[-1]
        else:
            self.commands.append(InputCommand(data, duration))
        self.commands.append(InputCommand(NUTRAL_REPORT, 0.0))
        return self

    def delay(self, seconds: float) -> Self:
        for cmd in self.commands:
            if isinstance(cmd, InputCommand):
                self.commands.append(InputCommand(cmd.data, seconds))
                return self

        self.commands.append(InputCommand(NUTRAL_REPORT, seconds))
        return self

    def end(self):
        if (self.loop_depth):
            raise UnclosedLoopError("Loop is not properly closed")
        pass

# ==================================================================================================== #

builder = MacroBuilder()
(
    builder
    .loop(15)
        .hold(Button.A, 0.1).delay(0.5)
        .hold(LS(Vector.UP), 5)
    .end_loop()
)