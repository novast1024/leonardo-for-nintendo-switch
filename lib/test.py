import serial
import time
from macro import *

ser = serial.Serial("COM6", 115200)
# ser.write(b"\x00\x00\x08\x80\x80\x80\x80\x00")

m = Macro(0.01).build(
    [LS(Vec2.UP * (i / 100)) for i in range(0, 100, 10)],
    [LS(Vec2.UP.rotate(i)) for i in range(0, 360, 10)],
    [LS(Vec2.UP * (i / 100)) for i in range(100, 0, -10)],

    # X, Y, ZR
)

for gamepad, duration in m.run():
    print(gamepad)
    ser.write(gamepad.to_hid_report())
    time.sleep(duration)
