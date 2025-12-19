from models.gamepad import Gamepad
from models.gamepad import BitFlags

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