from typing import Any, Self, final

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