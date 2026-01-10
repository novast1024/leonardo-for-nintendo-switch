import serial
import time

from macro import Macro, A
from codec import cobsr, crc8

ser = serial.Serial("COM6", 115200)
# ser.write(b"\x00\x00\x08\x80\x80\x80\x80\x00")

m = Macro().build(
    # [LS(Vec2.UP * (i / 100)) for i in range(0, 100, 10)],
    # [LS(Vec2.UP.rotate(i)) for i in range(0, 360, 10)],
    # [LS(Vec2.UP * (i / 100)) for i in range(100, 0, -10)],

    # X, Y, ZR

    (A >> 0.1, 0.1) * 3
)

for gamepad, duration in m.run():
    print(gamepad)
    data = gamepad.to_hid_report()
    ser.write(cobsr.encode(data + int.to_bytes(crc8.ccitt(data))) + b"\x00")
    time.sleep(duration)
