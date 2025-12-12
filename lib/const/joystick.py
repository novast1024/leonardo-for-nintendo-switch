from models.gamepad import Gamepad
from models.vector import Vec2

def ls(vec2: Vec2):
    return Gamepad(left_stick=vec2)

def rs(vec2: Vec2):
    return Gamepad(right_stick=vec2)