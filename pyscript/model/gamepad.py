from typing import Self, final
import itertools
import struct

from .intflag import Button, HatSwitch
from .vector import Vec2

@final
class Gamepad:
    __slots__ = ("buttons", "hat_switch", "left_stick", "right_stick")

    def __init__(
        self,
        buttons: Button = Button(0),
        hat_switch: HatSwitch = HatSwitch(0),
        left_stick: Vec2 = Vec2.ZERO,
        right_stick: Vec2 = Vec2.ZERO
    ) -> None:
        self.buttons = buttons
        self.hat_switch = hat_switch
        self.left_stick = left_stick
        self.right_stick = right_stick

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and\
            self.buttons == other.buttons and\
            self.hat_switch == other.hat_switch and\
            self.left_stick == other.left_stick and\
            self.right_stick == other.right_stick

    def __hash__(self) -> int:
        return hash((self.buttons, self.hat_switch, self.left_stick, self.right_stick))

    def __str__(self) -> str:
        return "+".join(itertools.chain(
            map(lambda f: f.name or "", itertools.chain(self.buttons, self.hat_switch)),
            () if self.left_stick is Vec2.ZERO else (f"LS({self.left_stick})",),
            () if self.right_stick is Vec2.ZERO else (f"RS({self.right_stick})",),
        )) or "NEUTRAL"

    def copy(self):
        return self.__class__(
            self.buttons,
            self.hat_switch,
            self.left_stick,
            self.right_stick,
        )

    def reset(self):
        self.buttons = Button(0)
        self.hat_switch = HatSwitch(0)
        self.left_stick = Vec2.ZERO
        self.right_stick = Vec2.ZERO

    def to_hid_report(self) -> bytes:
        return struct.pack("<HBBBBBB",
            self.buttons,
            _HatSwitch_to_HID_value[self.hat_switch],
            *map(
                lambda x: round((x + 1) / 2 * 255),
                itertools.chain(
                    self.left_stick.clamp_magnitude(),
                    self.right_stick.clamp_magnitude(),
                )
            ),
            0,
        )

    @classmethod
    def from_hid_report(cls, report: bytes) -> Self:
        lx, ly, rx, ry = map(lambda n: round(n / 255 * 2 - 1, 2), report[3:7])
        return cls(
            Button(int.from_bytes(report[0:2], "little")),
            _HID_value_to_HatSwitch[report[2]],
            Vec2(lx, ly),
            Vec2(rx, ry),
        )

_HatSwitch_to_HID_value = {
    0b0001: 0x0,
    0b1101: 0x0,
    0b1001: 0x1,
    0b1000: 0x2,
    0b1011: 0x2,
    0b1010: 0x3,
    0b0010: 0x4,
    0b1110: 0x4,
    0b0110: 0x5,
    0b0100: 0x6,
    0b0111: 0x6,
    0b0101: 0x7,
    0b0000: 0xf,
    0b0011: 0xf,
    0b1100: 0xf,
    0b1111: 0xf,
}

_HID_value_to_HatSwitch = {
    0x0: HatSwitch.UP,
    0x1: HatSwitch.UP|HatSwitch.RIGHT,
    0x2: HatSwitch.RIGHT,
    0x3: HatSwitch.DOWN|HatSwitch.RIGHT,
    0x4: HatSwitch.DOWN,
    0x5: HatSwitch.DOWN|HatSwitch.LEFT,
    0x6: HatSwitch.LEFT,
    0x7: HatSwitch.UP|HatSwitch.LEFT,
    0x8: HatSwitch(0),
    0x9: HatSwitch(0),
    0xa: HatSwitch(0),
    0xb: HatSwitch(0),
    0xc: HatSwitch(0),
    0xd: HatSwitch(0),
    0xe: HatSwitch(0),
    0xf: HatSwitch(0),
}