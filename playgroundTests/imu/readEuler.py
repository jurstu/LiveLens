from smbus2 import SMBus
import time
import struct

BNO055_ADDRESS = 0x28
OPR_MODE_ADDR = 0x3D
EULER_H_LSB = 0x1A  # Heading, Roll, Pitch (each 2 bytes)
CHIP_ID_ADDR = 0x00

CONFIG_MODE = 0x00
NDOF_MODE = 0x0C

bus = SMBus(5)

def write_register(reg, value):
    bus.write_byte_data(BNO055_ADDRESS, reg, value)
    time.sleep(0.01)

def read_euler():
    data = bus.read_i2c_block_data(BNO055_ADDRESS, EULER_H_LSB, 6)
    heading = struct.unpack('<h', bytes(data[0:2]))[0] / 16.0
    roll = struct.unpack('<h', bytes(data[2:4]))[0] / 16.0
    pitch = struct.unpack('<h', bytes(data[4:6]))[0] / 16.0
    return heading, roll, pitch

# Put in config mode to change modes
write_register(OPR_MODE_ADDR, CONFIG_MODE)
time.sleep(0.02)

# Set to NDOF (fused orientation)
write_register(OPR_MODE_ADDR, NDOF_MODE)
time.sleep(0.02)

print("Reading Euler angles (Heading, Roll, Pitch):")
while True:
    h, r, p = read_euler()
    print(f"Heading: {h:.2f}°, Roll: {r:.2f}°, Pitch: {p:.2f}°")
    time.sleep(0.01)
