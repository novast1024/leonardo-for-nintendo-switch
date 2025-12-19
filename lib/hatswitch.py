from models.gamepad import Gamepad
from models.gamepad import BitFlags

UP = Gamepad(hat_switch = BitFlags(0x01))
DOWN = Gamepad(hat_switch = BitFlags(0x02))
LEFT = Gamepad(hat_switch = BitFlags(0x04))
RIGHT = Gamepad(hat_switch = BitFlags(0x08))