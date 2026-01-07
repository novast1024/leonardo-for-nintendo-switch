from typing import Self, TypeAlias, NamedTuple
from collections.abc import Callable, Iterable, Generator
import itertools

from model import Gamepad, Button, HatSwitch, Vec2

class InputEvent:
    __slots__ = ("modifier",)

    def __init__(self, modifier: Callable[[Gamepad], None]) -> None:
        self.modifier = modifier

class BeginEvent(InputEvent):
    __slots__ = ()

class EndEvent(InputEvent):
    __slots__ = ()

class TimedEvent(NamedTuple):
    time: float
    event: InputEvent

class InputHandle():
    __slots__ = ("_modifiers",)

    def __init__(self, *modifiers: Callable[[Gamepad], None]) -> None:
        self._modifiers = modifiers

    def __add__(self, other: Self):
        return InputHandle(*self._modifiers, *other._modifiers)

    def __rshift__(self, duration: float):
        if duration <= 0:
            raise ValueError("Duration must be greater than 0.")

        return tuple(itertools.chain(
            (BeginEvent(i) for i in self._modifiers),
            (duration,),
            (EndEvent(i) for i in self._modifiers),
        ))

class ButtonPressHandle(InputHandle):
    __slots__ = ()

    def __init__(self, button: Button) -> None:
        def modifier(gamepad: Gamepad):
            gamepad.buttons |= button
        super().__init__(modifier)

class HatSwitchPressHandle(InputHandle):
    __slots__ = ()

    def __init__(self, hat_switch: HatSwitch) -> None:
        def modifier(gamepad: Gamepad):
            gamepad.hat_switch |= hat_switch
        super().__init__(modifier)

class LeftstickMoveHandle(InputHandle):
    __slots__ = ()

    def __init__(self, pos: Vec2) -> None:
        def modifier(gamepad: Gamepad):
            gamepad.left_stick = pos
        super().__init__(modifier)

class RightStickMoveHandle(InputHandle):
    __slots__ = ()

    def __init__(self, pos: Vec2) -> None:
        def modifier(gamepad: Gamepad):
            gamepad.right_stick = pos
        super().__init__(modifier)

class LeftStickPressHandle(ButtonPressHandle):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(Button.LS)

    def __call__(self, pos: Vec2):
        return LeftstickMoveHandle(pos)

class RightStickPressHandle(ButtonPressHandle):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(Button.RS)

    def __call__(self, pos: Vec2):
        return RightStickMoveHandle(pos)

Y = ButtonPressHandle(Button.Y)
B = ButtonPressHandle(Button.B)
A = ButtonPressHandle(Button.A)
X = ButtonPressHandle(Button.X)
L = ButtonPressHandle(Button.L)
R = ButtonPressHandle(Button.R)
ZL = ButtonPressHandle(Button.ZL)
ZR = ButtonPressHandle(Button.ZR)
MINUS = ButtonPressHandle(Button.MINUS)
PLUS = ButtonPressHandle(Button.PLUS)
LS = LeftStickPressHandle()
RS = RightStickPressHandle()
HOME = ButtonPressHandle(Button.HOME)
CAPTURE = ButtonPressHandle(Button.CAPTURE)

UP = HatSwitchPressHandle(HatSwitch.UP)
DOWN = HatSwitchPressHandle(HatSwitch.DOWN)
LEFT = HatSwitchPressHandle(HatSwitch.LEFT)
RIGHT = HatSwitchPressHandle(HatSwitch.RIGHT)

def flatten(data: Iterable[object]):
    stack = [iter(data)]
    while stack:
        it = stack[-1]
        try:
            obj = next(it)
        except StopIteration:
            stack.pop()
            continue
        if isinstance(obj, (list, tuple, Generator)):
            stack.append(iter(obj))
        else:
            yield obj

NestedInputSequence: TypeAlias = (
    InputHandle | InputEvent | float | int |
    list["NestedInputSequence"] |
    tuple["NestedInputSequence", ...] |
    Generator["NestedInputSequence", None, None]
)

class _MacroBuilder:
    def __init__(self,
        timed_events: list[TimedEvent],
        total_time: float,
        default_duration: float,
    ) -> None:
        self._timed_events = timed_events
        self._total_time = total_time
        self._default_duration = default_duration

    def __add__(self, other: Self):
        return self.__class__(
            [*itertools.chain(
                self._timed_events,
                map(lambda e: TimedEvent(e.time + self._total_time, e.event), other._timed_events)
            )],
            self._total_time + other._total_time,
            0
        )

    def build(self, *input_sequence: NestedInputSequence) -> Self:
        timed_events: list[TimedEvent] = []
        elapsed_time = 0
        for obj in flatten(input_sequence):
            if isinstance(obj, (float, int)):
                elapsed_time += obj
            elif isinstance(obj, InputEvent):
                timed_events.append(TimedEvent(elapsed_time, obj))
            elif isinstance(obj, InputHandle):
                if not self._default_duration:
                    raise ValueError("No default duration is set")
                for obj in obj >> self._default_duration:
                    if isinstance(obj, (float, int)):
                        elapsed_time += obj
                    else:
                        timed_events.append(TimedEvent(elapsed_time, obj))
            else:
                raise ValueError(f"Invalid type: {type(obj)}")

        if self._total_time > 0:
            self._timed_events.extend(timed_events)
            self._timed_events.sort(key = lambda timed_event: timed_event.time)
            self._total_time = self._total_time if self._total_time >= elapsed_time else elapsed_time
        else:
            self._timed_events = timed_events
            self._total_time = elapsed_time
        return self

    def run(self):
        # result: list[str] = []
        modifiers: list[Callable[[Gamepad], None]] = []
        gamepad = Gamepad()
        start_time = 0
        for time, event in self._timed_events:
            if start_time != time:
                for modifier in modifiers:
                    modifier(gamepad)
                # result.append(f"{gamepad} >> {time - start_time:0.2f}")
                yield gamepad, time - start_time
                start_time = time
                gamepad.reset()
            if type(event) is BeginEvent:
                modifiers.append(event.modifier)
            else:
                modifiers.remove(event.modifier)
        for modifier in modifiers:
            modifier(gamepad)
        # result.append(f"{gamepad} >> {self._total_time - start_time:0.2f}")
        yield gamepad, self._total_time - start_time
        # print(*result, sep = "\n")


def Macro(default_duration: float | None = None):
    return _MacroBuilder([], 0, default_duration or 0)