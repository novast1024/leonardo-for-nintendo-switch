from enum import IntFlag
from typing import final

@final
class Button(IntFlag):
    Y =       0x0001
    B =       0x0002
    A =       0x0004
    X =       0x0008
    L =       0x0010
    R =       0x0020
    ZL =      0x0040
    ZR =      0x0080
    MINUS =   0x0100
    PLUS =    0x0200
    LS =      0x0400
    RS =      0x0800
    HOME =    0x1000
    CAPTURE = 0x2000

@final
class HatSwitch(IntFlag):
    UP =    0b0001
    DOWN =  0b0010
    LEFT =  0b0100
    RIGHT = 0b1000