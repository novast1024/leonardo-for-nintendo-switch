# from models.gamepad import Button, LS, RS, Gamepad
from models.vector import Vec2
from joystick import ls
from button import A

print(A.__bytes__().hex(" "))
print(ls(Vec2.UP+Vec2.RIGHT).__bytes__().hex(" "))

# print(LS(Vec2.UP).__bytes__().hex(" "))
# print(LS(Vec2.UP + Vec2.RIGHT).__bytes__().hex(" "))
# print(LS(Vec2.RIGHT).__bytes__().hex(" "))
# print(LS(Vec2.DOWN + Vec2.RIGHT).__bytes__().hex(" "))
# print(LS(Vec2.DOWN).__bytes__().hex(" "))
# print(LS(Vec2.DOWN + Vec2.LEFT).__bytes__().hex(" "))
# print(LS(Vec2.LEFT).__bytes__().hex(" "))
# print(LS(Vec2.UP + Vec2.LEFT).__bytes__().hex(" "))




