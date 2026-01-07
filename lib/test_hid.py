import time
import hid # pip install hidapi
import serial

from codec import cobsr

ser = serial.Serial("COM3", 115200)

dev_dict_list = hid.enumerate()
dev_dict_list.sort(key=lambda it: it["product_string"])
for i, dev_dict in enumerate(dev_dict_list):
    print(f"{i} vid=0x{dev_dict["vendor_id"]:04x} pid=0x{dev_dict["product_id"]:04x} {dev_dict["product_string"]}")

try:
    idx = int(input(f"Select a device (0-{len(dev_dict_list)-1}): "))
    dev_dict = dev_dict_list[idx]
    device = hid.device()
    print(f"Opening the {dev_dict["product_string"]}")
    device.open(dev_dict["vendor_id"], dev_dict["product_id"])
    device.set_nonblocking(1)

    seconds = float(input("Enter seconds: "))
    start = time.perf_counter()
    while time.perf_counter() - start < seconds:
        if report := device.read(64):
            data = bytes(report)
            print(data.hex(" "))
            ser.write(cobsr.encode(data) + b"\x00")
    print(f"Closing the {dev_dict["product_string"]}")
    device.close()

except (ValueError, IndexError, IOError) as e:
    print(e)