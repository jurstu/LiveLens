import numpy as np
import time

from MSP import MSP
from liveLens.view import View
from liveLens.camera import Camera
from loggingSetup import getLogger
from webView.webView import UiGen



logger = getLogger(__name__)

class LiveLens:
    def __init__(self):
        self.view = View()
        self.view.worldStore.generateFloor(np.array([0, 0, 0]), 3, 0.05)
        R = 1
        eps = 0.01
        self.position = [eps, eps, eps]
        
        self.view.setCameraPosAtt(self.position, 0, 0, 0)
        self.view.drawWorld()
        self.imu = MSP("/dev/ttyACM1")
        self.cam = Camera(2, [1280, 720])



    def fuse(self):
        self.view.setCameraPosAtt(self.position, -self.imu.roll.value, self.imu.pitch.value, self.imu.yaw.value)
        lastImage = self.cam.latest_frame
        ll.view.canvas = lastImage
        ll.view.drawWorld(clearCanvas = False)


if __name__ == "__main__":
    ug = UiGen(1280, 720)
    ug.run()

    ll = LiveLens()

    while(1):

        #ll.view.setCameraPosAtt(ll.position, -ll.imu.roll.value, ll.imu.pitch.value, ll.imu.yaw.value)
        #logger.info(ll.view.cameraPos)
        ug.moveMarkerAndShowIt(ll.imu.lat.value, ll.imu.lon.value)
        ll.fuse()
        ug.lastImage = ll.view.canvas
        time.sleep(0.01)