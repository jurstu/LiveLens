import numpy as np
import json as js
import logging
from loggingSetup import getLogger

logger = getLogger(__name__)

class WorldStore:
    def __init__(self):
        logger.info("Created a world object")

    def load(self, path="./world.json"):
        try:
            with open(path, "r") as f:
                self.world = js.load(f)
            logger.debug("loaded world json file")
        except Exception as e:
            logger.error("Couldn't load world", exc_info=False)
            return 
        


if __name__ == "__main__":
    ws = WorldStore()
    ws.load()