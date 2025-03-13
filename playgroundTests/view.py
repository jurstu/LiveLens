import cv2
import cv2.text
import numpy as np
from pinholeCamera import PinholeCamera, getExampleK
from worldStore import WorldStore
from loggingSetup import getLogger

logger = getLogger(__name__)

class View:
    def __init__(self, width:int = 1280, height:int = 720, bgColor:list[int] = (255, 255, 255)):
        self.width = width
        self.height = height
        self.bgColor = bgColor
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.canvas[:] = np.array(self.bgColor, dtype=np.uint8)

        self.pinholeCamera = PinholeCamera(getExampleK())
        self.worldStore = WorldStore()
        self.worldStore.load()
        self.cameraPos = [0, 0, 0]
        self.roll = 0
        self.pitch = 0
        self.yaw = 0


    def setCameraPosAtt(self, cameraPos, roll, pitch, yaw):
        self.cameraPos = cameraPos
        self.roll = roll        
        self.pitch = pitch
        self.yaw = yaw

    def drawWorld(self):
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.canvas[:] = np.array(self.bgColor, dtype=np.uint8)

        points = self.worldStore.pointList
        pointsNp = []
        for pt in points:
            pointsNp.append([pt.x, pt.y, pt.z])
        pointsNp = np.array(pointsNp)
        
        # TODO check edge-case where there are no points to calculate
        pixelPositions = self.pinholeCamera.getProjections(pointsNp, self.roll, self.pitch, self.yaw, self.cameraPos)
        pixelPositions = pixelPositions.astype(np.int32)
        #pixelPositions += np.array([self.width/2, -self.height/2], dtype=np.int32)

        for i, pixel in enumerate(pixelPositions):
            #logger.debug(pixel)
            cv2.circle(self.canvas, pixel, 5, (0, 0, 0))

        lines = []
        lines.append("roll: {:0.2f}".format(self.roll))
        lines.append("pitch: {:0.2f}".format(self.pitch))
        lines.append("yaw: {:0.2f}".format(self.yaw))
        lines.append("x: {:0.2f}".format(self.cameraPos[0]))
        lines.append("y: {:0.2f}".format(self.cameraPos[1]))
        lines.append("z: {:0.2f}".format(self.cameraPos[2]))
        
        for i, line in enumerate(lines):
            cv2.putText(self.canvas, line, (self.width//2, 40 + i*12), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1)





if __name__ == "__main__":
    view = View()
    view.worldStore.generateFloor(np.array([0, 0, 0]), 3, 0.05)
    R = 1
    position = [-R, 0, 0.1]
    view.setCameraPosAtt(position, 0, 0, 0)

    angle = 0
    while True:
        angle += 1
        
        position = [-R * np.cos(np.deg2rad(angle)), R * np.sin(np.deg2rad(angle)), 0.1]
        view.setCameraPosAtt(position, 0, 0, angle + 90)
        view.drawWorld()
        cv2.imshow("main view", view.canvas)
        
        if cv2.waitKey(33) & 0xFF == 27:  # Press 'ESC' to exit
            break
        
        

    cv2.destroyAllWindows()