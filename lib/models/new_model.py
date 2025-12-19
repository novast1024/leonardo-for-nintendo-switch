from typing import Protocol


class InputEvent(Protocol):
    def apply(self): ...


class ButtonEvent:
    def __init__(self, name: str) -> None:
        match (name):
            case "Y":
                self.value = 0x0001
            case _:
                raise AssertionError("not reached")



A = ButtonEvent("A")


