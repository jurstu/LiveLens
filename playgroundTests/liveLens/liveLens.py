import time

from imu.bno055 import BNO055
from liveLens.camera import Camera

class LiveLens:
    def __init__(self):
        pass
    



if __name__ == "__main__":
    imu = BNO055()
    cam = Camera(2, [640, 480])
    while(1):
        time.sleep(1)