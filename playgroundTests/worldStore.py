import numpy as np
import json as js
import logging
from loggingSetup import getLogger
from threeDeePoint import ThreeDeePoint

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
            self.objectList = [0] * len(self.objects)
            for i, object in enumerate(self.objects):
                objType = object["type"]
                objName = object["name"]
                if(objType == "point"):
                    position = object["position"]
                    self.objectList[i] = ThreeDeePoint(position[0], 
                                                    position[1], 
                                                    position[2], 
                                                    objName)
        except Exception as e:
            logger.error("Could not load the whole world")
            logger.exception(e)
            return
        
        logger.debug("Loaded world objects")

            
        




if __name__ == "__main__":
    ws = WorldStore()
    ws.load()