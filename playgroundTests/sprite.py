import numpy as np
import cv2
from loggingSetup import getLogger

logger = getLogger(__name__)

class Sprite:
    def __init__(self, points: np.ndarray, filePath: str, name: str = "", ):
        self.points = points
        self.filePath = filePath
        self.name = name
        self.load()

    def load(self):
        try:
            self.image = cv2.imread(self.filePath)

        except:
            logger.error("Couldn't load sprite", exc_info=True)
            self.image = np.array([100, 100, 3])




if __name__ == "__main__":
    s = Sprite(np.array([]), "./assets/aruco.png")
    cv2.imshow("images", s.image)
    cv2.waitKey(2000)

