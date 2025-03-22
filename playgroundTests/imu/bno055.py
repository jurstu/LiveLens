from smbus2 import SMBus
import time
import struct
from threading import Thread
from imu.loggingSetup import getLogger
logger = getLogger(__name__)

class BNO055:
    BNO055_ADDRESS = 0x28
    OPR_MODE_ADDR = 0x3D
    EULER_H_LSB = 0x1A  # Heading, Roll, Pitch (each 2 bytes)
    CHIP_ID_ADDR = 0x00
    CONFIG_MODE = 0x00
    NDOF_MODE = 0x0C

    def __init__(self, i2c_dev:int =5):
        self.bus = SMBus(5)
        self.write_register(BNO055.OPR_MODE_ADDR, BNO055.CONFIG_MODE)
        self.write_register(BNO055.OPR_MODE_ADDR, BNO055.NDOF_MODE)
        time.sleep(0.02)
        self.heading = 0
        self.roll = 0
        self.pitch = 0
        self.t = Thread(target = self.run, daemon=True)
        self.t.start()
        
    def write_register(self, reg=int, value=int):
        self.bus.write_byte_data(BNO055.BNO055_ADDRESS, reg, value)

    def read_euler(self):
        data = self.bus.read_i2c_block_data(BNO055.BNO055_ADDRESS, BNO055.EULER_H_LSB, 6)
        self.heading = struct.unpack('<h', bytes(data[0:2]))[0] / 16.0
        self.roll = struct.unpack('<h', bytes(data[2:4]))[0] / 16.0
        self.pitch = struct.unpack('<h', bytes(data[4:6]))[0] / 16.0
    
    def run(self):
        logger.debug("starting BNO055")
        while True:
            self.read_euler()
            #logger.debug(f"Heading: {self.heading:.2f}°, Roll: {self.roll:.2f}°, Pitch: {self.pitch:.2f}°")
            time.sleep(0.01)



if __name__ == "__main__":
    imu = BNO055()
    while(1):
        time.sleep(1)