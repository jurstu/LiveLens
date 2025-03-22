import cv2
import numpy as np
import time

from liveLens.pinholeCamera import PinholeCamera, getExampleK
from liveLens.worldStore import WorldStore
from liveLens.loggingSetup import getLogger
from liveLens.threeDeePoint import ThreeDeePoint
from liveLens.sprite import Sprite




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


    def drawPoint(self, point:ThreeDeePoint, dist:np.ndarray):
        #logger.debug(dist)
        cv2.circle(self.canvas, dist, 5, (0, 0, 0))

    def drawSprite(self, sprite:Sprite, dst:np.ndarray):
        mv = 8
        hh, ww = sprite.image.shape[:2]
        src = [[mv, mv], [mv, ww-mv], [hh-mv, ww-mv], [hh-mv, mv]]

        src = np.array(src, np.float32)
        dst = np.array(dst, np.float32)
        M = cv2.getPerspectiveTransform(src, dst)
        warp = cv2.warpPerspective(sprite.image, M, (self.width, self.height))
        
        mask = np.zeros((self.height, self.width), dtype=np.uint8)
        cv2.fillPoly(mask, [dst.astype(np.int32)], 255)
        
        cv2.copyTo(warp, mask, self.canvas)

        #mask_inv = cv2.bitwise_not(mask)
        #warpedSpriteOnly = cv2.bitwise_and(warp, warp, mask=mask)
        #canvasBg = cv2.bitwise_and(self.canvas, self.canvas, mask=mask_inv)
        #self.canvas = cv2.add(canvasBg, warpedSpriteOnly)


    def drawWorld(self):
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.canvas[:] = 255
        

        
        points = self.worldStore.pointList
        sprites = self.worldStore.spriteList
        cp = [self.cameraPos[1], -self.cameraPos[2], -self.cameraPos[0]]
        combinedList = sorted(points + sprites, key=lambda obj: -obj.getDistNorm(cp))
        

        rawPointsList = []
        for object in combinedList:
            match object:
                case Sprite():
                    if(not object.isSpriteFacingCam(cp)):
                        continue
                    for i in range(4):
                        rawPointsList.append([object.points[i][0], object.points[i][1], object.points[i][2]])
                case ThreeDeePoint():
                    rawPointsList.append([object.x, object.y, object.z])
                case _:
                    logger.error("object type not handled by renderer")

        rawPointsList = np.array(rawPointsList)
        pp, z = self.pinholeCamera.getProjections(rawPointsList, self.roll, self.pitch, self.yaw, self.cameraPos)
        pp = pp.astype(np.int32)

        counter = 0
        for object in combinedList:
            match object:
                case Sprite():
                    if(not object.isSpriteFacingCam(cp)):
                        continue
                    zs = z[counter:counter+4]
                    dist = pp[counter:counter+4]
                    counter+=4
                    
                    self.drawSprite(object, dist)
                case ThreeDeePoint():
                    dist = pp[counter]
                    if(z[counter] > 0):
                        self.drawPoint(object, dist)
                    counter+=1
                    
                    
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
    from webView.webView import UiGen
    ug = UiGen(1280, 720)
    ug.run()
    view = View()
    view.worldStore.generateFloor(np.array([0, 0, 0]), 3, 0.05)
    R = 1
    position = [-R, 0, 0.1]
    view.setCameraPosAtt(position, 0, 0, 0)

    angle = 0
    tt = time.time()
    while True:
        angle += 1
        
        print(angle, "{:02.2f}".format(angle/(time.time()-tt)))
        position = [-R * np.cos(np.deg2rad(angle)), R * np.sin(np.deg2rad(angle)), 0.3]
        view.setCameraPosAtt(position, 0, 0, angle + 90)
        view.drawWorld()
        ug.lastImage = view.canvas
        #cv2.imshow("main view", view.canvas)
        
        #if cv2.waitKey(16) & 0xFF == 27:  # Press 'ESC' to exit
        #    break
        #time.sleep(0.033)
        
        

    cv2.destroyAllWindows()
