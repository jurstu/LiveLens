import numpy as np
import json as js
import logging
from loggingSetup import getLogger
from liveLens.threeDeePoint import ThreeDeePoint
from liveLens.sprite import Sprite
from liveLens.line import Line
from liveLens.sphere import Sphere

logger = getLogger(__name__)

class WorldStore:
    def __init__(self):
        logger.info("Created a world object")

    def load(self, path: str = "./world.json"):
        try:
            with open(path, "r") as f:
                self.world = js.load(f)
            logger.debug("Loaded world json file")
        except Exception as e:
            logger.error("Couldn't load world", exc_info=False)
            return 

        try:
            self.versionMajor = self.world["version"]["major"]
            self.versionMinor = self.world["version"]["minor"]

            self.objects = self.world["objects"]
            self.pointList = []
            self.spriteList = []
            self.lineList = []
            self.sphereList = []

            self.horizonList = []
            self.horizonFlatText = []

            for i, object in enumerate(self.objects):
                objType = object["type"]
                objName = object["name"]
                if(objType == "point"):
                    position = object["position"]
                    self.pointList.append(ThreeDeePoint(position[0], 
                                                    position[1], 
                                                    position[2], 
                                                    objName))
            
                if(objType == "sprite"):
                    points = object["points"]
                    visible = object["visible"]
                    texturePath = object["texturePath"]
                    sprite = Sprite(points, texturePath, objName, visible)
                    self.spriteList.append(sprite)
                    logger.debug("Loaded a sprite texture from " + texturePath)

                if(objType == "line"):
                    p1 = object["p1"]
                    p2 = object["p2"]
                    p1 = ThreeDeePoint(p1[0], 
                                       p1[1], 
                                       p1[2], 
                                       "p1")
                    p2 = ThreeDeePoint(p2[0], 
                                       p2[1], 
                                       p2[2], 
                                       "p2")
                    visible = object["visible"]
                    color = object["color"]
                    line = Line(p1, p2, color, objName)
                    self.lineList.append(line)

                if(objType == "sphere"):
                    p = object["p"]
                    p  = ThreeDeePoint(p[0], 
                                       p[1], 
                                       p[2], 
                                       "p")
                    r = object["r"]
                    visible = object["visible"]
                    color = object["color"]
                    sphere = Sphere(p.x, p.y, p.z, r, color, objName)
                    self.sphereList.append(sphere)

        except Exception as e:
            logger.error("Could not load the whole world")
            logger.exception(e)
            return
        
        logger.debug("Loaded world objects")

    def _outputListOfPoints(self):
        for p in self.pointList:
            logger.info(p)
        

    def generateFloor(self, pos: np.ndarray, squareSize: int, spacing: int = 0.3):
        self.pointList = []
        for x in range(0, squareSize):
            for z in range(0, squareSize):

                point = ThreeDeePoint(*(pos + np.array([x*spacing, 0, z*spacing])))

                self.pointList.append(point)
        import time
        if(int(time.time()) %10 > 5):
            for x in range(0, squareSize):
                    for z in range(0, squareSize):

                        point = ThreeDeePoint(*(pos + np.array([-x*spacing, 0, -z*spacing])))

                        self.pointList.append(point)


if __name__ == "__main__":
    ws = WorldStore()
    ws.load()
    ws._outputListOfPoints()