import numpy as np
import time

from MSP import MSP
from liveLens.view import View
from liveLens.camera import Camera
from liveLens.loggingSetup import getLogger
from webView.webView import UiGen



logger = getLogger(__name__)

class LiveLens:
    def __init__(self):
        self.view = View()
        self.view.worldStore.generateFloor(np.array([0, 0, 0]), 3, 0.05)
        R = 1
        self.position = [-R, 0, 0.1]
        self.view.setCameraPosAtt(self.position, 0, 0, 0)
        self.view.drawWorld()

        imu = MSP("/dev/ttyACM0")

        self.cam = Camera(3, [1280, 720])

    def fuse(self):
        lastImage = self.cam.latest_frame
        ll.view.canvas = lastImage
        ll.view.drawWorld(clearCanvas = False)


if __name__ == "__main__":
    ug = UiGen(1280, 720)
    ug.run()

    ll = LiveLens()

    while(1):
        ll.view.setCameraPosAtt(ll.position, -ll.imu.roll, ll.imu.pitch, ll.imu.heading)
        ll.fuse()
        ug.lastImage = ll.view.canvas
        #time.sleep(0.01)