import serial
from codec import cobsr, crc8

class SerialHandle:
    def __init__(self) -> None:
        self.serial = serial.Serial("COM6", 115200)

    def send(self, data: bytes):
        self.serial.write(cobsr.encode(data + int.to_bytes(crc8.ccitt(data))) + b"\x00")