import cv2
import numpy as np
from pinholeCamera import PinholeCamera, getExampleK
from worldStore import WorldStore
from loggingSetup import getLogger
from threeDeePoint import ThreeDeePoint
from sprite import Sprite

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


    def drawPoint(self, point:ThreeDeePoint):
        point = np.array([[point.x, point.y, point.z]])
        pp = self.pinholeCamera.getProjections(point, self.roll, self.pitch, self.yaw, self.cameraPos)
        pp = pp.astype(np.int32)
        cv2.circle(self.canvas, pp[0], 5, (0, 0, 0))

    def drawSprite(self, sprite:Sprite):
        cp = [self.cameraPos[1], -self.cameraPos[2], -self.cameraPos[0]]
        if(not sprite.isSpriteFacingCam(cp)):
            return
        corners = []
        for i in range(4):
            corners.append([sprite.points[i][0], sprite.points[i][1], sprite.points[i][2]])
        corners = np.array(corners)
        pp = self.pinholeCamera.getProjections(corners, self.roll, self.pitch, self.yaw, self.cameraPos)
        pp = pp.astype(np.int32)
        hh, ww = sprite.image.shape[:2]
        
        mv = 8
        src = [[mv, mv], [mv, ww-mv], [hh-mv, ww-mv], [hh-mv, mv]]
        dst = []
        for i in range(4):
            dst.append(pp[i])
        src = np.array(src, np.float32)
        dst = np.array(dst, np.float32)
        M = cv2.getPerspectiveTransform(src, dst)
        warp = cv2.warpPerspective(sprite.image, M, (self.width, self.height))
        mask = np.zeros((self.height, self.width), dtype=np.uint8)
        cv2.fillPoly(mask, [dst.astype(np.int32)], 255)
        mask_inv = cv2.bitwise_not(mask)
        warpedSpriteOnly = cv2.bitwise_and(warp, warp, mask=mask)
        canvasBg = cv2.bitwise_and(self.canvas, self.canvas, mask=mask_inv)
        self.canvas = cv2.add(canvasBg, warpedSpriteOnly)


    def drawWorld(self):
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.canvas[:] = np.array(self.bgColor, dtype=np.uint8)



        points = self.worldStore.pointList
        sprites = self.worldStore.spriteList
        cp = [self.cameraPos[1], -self.cameraPos[2], -self.cameraPos[0]]
        combinedList = sorted(points + sprites, key=lambda obj: -obj.getDistNorm(cp))

        for object in combinedList:
            match object:
                case Sprite():
                    self.drawSprite(object)
                case ThreeDeePoint():
                    self.drawPoint(object)
                case _:
                    logger.error("object type not handled by renderer")
                    
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
        
        position = [-R * np.cos(np.deg2rad(angle)), R * np.sin(np.deg2rad(angle)), 0.3]
        view.setCameraPosAtt(position, 0, 0, angle + 90)
        view.drawWorld()
        cv2.imshow("main view", view.canvas)
        
        if cv2.waitKey(16) & 0xFF == 27:  # Press 'ESC' to exit
            break
        
        

    cv2.destroyAllWindows()
