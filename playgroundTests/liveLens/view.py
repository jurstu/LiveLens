import cv2
import numpy as np
import time
import colorsys

from liveLens.pinholeCamera import PinholeCamera, getExampleK
from liveLens.worldStore import WorldStore
from loggingSetup import getLogger
from liveLens.threeDeePoint import ThreeDeePoint, HorizonFlatText
from liveLens.sprite import Sprite
from liveLens.line import Line
from liveLens.sphere import Sphere



logger = getLogger(__name__)


def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))


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


    def drawSphere(self, sphere:Sphere, dist:np.ndarray, z: float):
        #logger.debug(dist)
        c = sphere.color
        p = dist[0]
        fx = self.pinholeCamera.K[0, 0]
        fy = self.pinholeCamera.K[1, 1]
        r = sphere.r
        rx = fx * r / z
        ry = fy * r / z
        r = int((rx + ry) / 2)
        #r = int(np.sqrt((p[0] - pr[0])**2 + (p[1] - pr[1])**2))
        #r = int(np.linalg.norm([p[0] - pr[0], p[1] - pr[1]]))
        cv2.circle(self.canvas, p, r, c, thickness=-1)

    def drawPoint(self, point:ThreeDeePoint, dist:np.ndarray):
        #logger.debug(dist)
        cv2.circle(self.canvas, dist, 5, (0, 0, 0))

    def drawHorizonFlatText(self, text:HorizonFlatText, dist:np.ndarray):
        #logger.debug(dist)
        font = cv2.FONT_HERSHEY_DUPLEX
        size = 1

        textsize = cv2.getTextSize(text.text, font, 1, 2)[0]
        textX = int(dist[0] - (textsize[0] / 2))
        textY = int(dist[1] + (textsize[1] / 2)) + text.yOffset
        
        cv2.putText(self.canvas, text.text, (textX, textY), font, 1, (0, 0, 0), 6)
        cv2.putText(self.canvas, text.text, (textX, textY), font, 1, text.color, 2)
        
        #cv2.circle(self.canvas, dist, 5, (0, 0, 0))



    def drawLine(self, line:Line, dist:np.ndarray):
        #logger.debug(dist)
        c = line.color
        distOrig = dist.copy()
        for p in dist:
            if np.isnan(p[0]) or np.isnan(p[1]):
                logger.critical("number is NaN")
            
        dist = [[int(x[0]), int(x[1])] for x in dist]

        c = [int(x) for x in c]
        try:
            cv2.line(self.canvas, dist[0], dist[1], [c[0], c[1], c[2]], 2)
        except:
            logger.critical(f"dist was {dist}, original values {distOrig}")


    def drawSprite(self, sprite:Sprite, dst:np.ndarray):
        if(sprite.visible == False):
            return
        mv = 8
        hh, ww = sprite.image.shape[:2]
        src = np.array([[mv, mv], [mv, ww - mv], [hh - mv, ww - mv], [hh - mv, mv]], dtype=np.float32)
        dst = np.array(dst, np.float32)

        x, y, w, h = cv2.boundingRect(dst)  # Find bounding box of destination quad
        dst_roi = dst.copy()
        dst_roi[:, 0] -= x  # Shift points to ROI-relative coordinates
        dst_roi[:, 1] -= y
        #cv2.rectangle(self.canvas, (x, y), (x+w, y+h), (128, 0, 255), 2)

        M = cv2.getPerspectiveTransform(src, dst_roi)
        warp = cv2.warpPerspective(sprite.image, M, (w, h))
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [dst_roi.astype(np.int32)], 255)

        roi = self.canvas[y:y+h, x:x+w]
        cv2.copyTo(warp, mask, roi)


    def generateHorizon(self):
        self.worldStore.horizonList = []
        self.worldStore.horizonFlatText = []

        center = self.cameraPos
        R = 5
        segments = 24

        for i in range(segments):
            a0 = i     * 360/segments
            a1 = (i+1) * 360/segments

            a0r = np.deg2rad(a0)
            a1r = np.deg2rad(a1)

            c = center
            p0 = [c[0] + R*np.cos(a0r), c[1] + R*np.sin(a0r), c[2]]
            p1 = [c[0] + R*np.cos(a1r), c[1] + R*np.sin(a1r), c[2]]

            self.worldStore.horizonList.append(Line(
                ThreeDeePoint(p0[0], p0[1], p0[2]),
                ThreeDeePoint(p1[0], p1[1], p1[2]),
                    [0, 255, 0] #hsv2rgb(i/segments, 1, 1)
                ))

            if(a0 % 30 == 0):
                self.worldStore.horizonFlatText.append(
                    HorizonFlatText(p0[0], p0[1], p0[2] + 0.05, [0, 255, 0], str(int(360 - a0)), "", yOffset=-20)
                )
                self.worldStore.horizonList.append(Line(
                ThreeDeePoint(p0[0], p0[1], p0[2]-0.1),
                ThreeDeePoint(p0[0], p0[1], p0[2]+0.1),
                    [0, 0, 0] #hsv2rgb(i/segments, 1, 1)
                ))

            
            if a0 == 0 or a0 == 360:
                self.worldStore.horizonFlatText.append(
                    HorizonFlatText(p0[0], p0[1], p0[2], [0, 255, 0], "N", "", yOffset=30)
                )
            if a0 == 90:
                self.worldStore.horizonFlatText.append(
                    HorizonFlatText(p0[0], p0[1], p0[2], [0, 255, 0], "E", "", yOffset=30)
                )
            if a0 == 180:
                self.worldStore.horizonFlatText.append(
                    HorizonFlatText(p0[0], p0[1], p0[2], [0, 255, 0], "S", "", yOffset=30)
                )
            if a0 == 270:
                self.worldStore.horizonFlatText.append(
                    HorizonFlatText(p0[0], p0[1], p0[2], [0, 255, 0], "W", "", yOffset=30)
                )
            
            




    def drawWorld(self, clearCanvas:bool = True):
        if clearCanvas:
            self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            self.canvas[:] = 255

        self.generateHorizon()

        points = self.worldStore.pointList
        sprites = self.worldStore.spriteList
        lines = self.worldStore.lineList
        spheres = self.worldStore.sphereList
        horizon = self.worldStore.horizonList
        horizonFlatText = self.worldStore.horizonFlatText

        # the original one
        cp = [self.cameraPos[1], -self.cameraPos[2], -self.cameraPos[0]]
        # TODO this needs to get fixed
        combinedList = sorted(points + sprites + lines + spheres + horizon + horizonFlatText, key=lambda obj: -obj.getDistNorm(cp))
        

        rawPointsList = []
        for object in combinedList:
            match object:
                case Sprite():
                    if(not object.isSpriteFacingCam(cp)):
                        continue
                    for i in range(4):
                        rawPointsList.append([object.points[i][0], object.points[i][1], object.points[i][2]])
                case ThreeDeePoint() | HorizonFlatText():
                    rawPointsList.append([object.x, object.y, object.z])
                case Line():
                    rawPointsList.append([object.p1.x, object.p1.y, object.p1.z])
                    rawPointsList.append([object.p2.x, object.p2.y, object.p2.z])
                case Sphere():
                    rawPointsList.append([object.x, object.y, object.z])
                case _:
                    logger.error("object type not handled by renderer")

        rawPointsList = np.array(rawPointsList)
        pp, z = self.pinholeCamera.getProjections(rawPointsList, self.roll, self.pitch, self.yaw, self.cameraPos)
        # filter out floats from outer space
        # TODO
        pp = pp.astype(int)

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
                    
                case HorizonFlatText():
                    dist = pp[counter]
                    if(z[counter] > 0):
                        self.drawHorizonFlatText(object, dist)
                    counter+=1

                case Line():
                    dist = pp[counter:counter+2]
                    if(z[counter] > 0 and z[counter+1] > 0):
                        self.drawLine(object, dist)
                    counter+=2

                case Sphere():

                    dist = pp[counter:counter+1]
                    if(z[counter] > 0.01):
                        self.drawSphere(object, dist, z[counter])
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
        angle += 0.5
        
        #logger.info("{:02.2f}, {:02.2f}".format(angle, angle/(time.time()-tt)))
        R = 1 + 0.0 * np.sin(np.deg2rad(3*angle))
        position = [0 - R * np.cos(np.deg2rad(angle)), R * np.sin(np.deg2rad(angle)), 0.3]
        
        view.setCameraPosAtt(position, 0, 0, 1*angle + 90)
        try:
            view.drawWorld()
            ug.lastImage = view.canvas
            time.sleep(0.033)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.warning("couldn't draw the world: " + str(e))
        
        

    cv2.destroyAllWindows()
