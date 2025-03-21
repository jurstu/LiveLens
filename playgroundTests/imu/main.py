import time
#import board
#import busio
#import adafruit_bno055






from smbus2 import SMBus

BNO055_ADDRESS = 0x28  # or 0x29 depending on your wiring
BNO055_CHIP_ID_ADDR = 0x00

bus = SMBus(5)  # try 0 or 2 if 1 doesn’t work

chip_id = bus.read_byte_data(BNO055_ADDRESS, BNO055_CHIP_ID_ADDR)

if chip_id == 0xA0:
    print("BNO055 detected!")
else:
    print(f"Unexpected chip ID: 0x{chip_id:02X}")



exit(0)
# Set up I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Create sensor object
sensor = adafruit_bno055.BNO055_I2C(i2c)

# Read some sensor values
while True:
    print("Temperature: {} C".format(sensor.temperature))
    print("Accelerometer (m/s^2): {}".format(sensor.acceleration))
    print("Gyroscope (rad/s): {}".format(sensor.gyro))
    print("Magnetometer (microteslas): {}".format(sensor.magnetic))
    print("Euler angle: {}".format(sensor.euler))
    print("Quaternion: {}".format(sensor.quaternion))
    print("Linear acceleration: {}".format(sensor.linear_acceleration))
    print("Gravity: {}".format(sensor.gravity))
    print("")

    time.sleep(1)

