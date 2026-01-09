from typing import Any, Self, final
from collections.abc import Generator
import math

@final
class Vec2:
    ZERO: Self
    UP: Self
    DOWN: Self
    LEFT: Self
    RIGHT: Self

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
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.x - other.x, self.y - other.y)

    def __mul__(self, value: float) -> Self:
        return self.__class__(self.x * value, self.y * value)

    def __truediv__(self, value: float) -> Self:
        return self.__class__(self.x / value, self.y / value)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.x == other.x and self.y == other.y

    def __iter__(self) -> Generator[float, None, None]:
        yield self.x
        yield self.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __str__(self) -> str:
        return f"Vec2({self.x:0.1f}, {self.y:0.1f})"

    def __repr__(self) -> str:
        return f"Vec2({self.x}, {self.y})"

    def rotate(self, degrees: float) -> Self:
        """
        Rotate the vector by the given angle in degrees (clockwise).
        Returns a new Vec2 instance with rotated coordinates.
        """
        if (degrees % 360 == 0) or (self.x == 0 and self.y == 0):
            return self
        rad = math.radians(degrees)
        cos = math.cos(rad)
        sin = math.sin(rad)
        return self.__class__(
            self.x * cos - self.y * sin,
            self.x * sin + self.y * cos
        )

    def clamp_magnitude(self, max_magnitude: float = 1) -> Self:
        """
        Limit the vector's magnitude to the specified maximum.
        Returns a new Vec2 instance with adjusted length if necessary.
        """
        mag = math.hypot(self.x, self.y)
        if mag <= max_magnitude:
            return self
        else:
            scale = max_magnitude / mag
            return self.__class__(self.x * scale, self.y * scale)

Vec2.ZERO = Vec2(0, 0)
Vec2.UP = Vec2(0, -1)
Vec2.DOWN = Vec2(0, 1)
Vec2.LEFT = Vec2(-1, 0)
Vec2.RIGHT = Vec2(1, 0)

_cached_Vec2 = {
    (0, 0): Vec2.ZERO,
    (0, -1): Vec2.UP,
    (0, 1): Vec2.DOWN,
    (-1, 0): Vec2.LEFT,
    (1, 0): Vec2.RIGHT,
}

setattr(Vec2, "__new__", lambda cls, x, y: _cached_Vec2.get((x, y)) or super(Vec2, cls).__new__(cls))