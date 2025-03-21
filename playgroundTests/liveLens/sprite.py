import numpy as np
import cv2
from liveLens.loggingSetup import getLogger

logger = getLogger(__name__)

class Sprite:
    def __init__(self, points: np.ndarray, filePath: str, name: str = "", ):
        self.points = points
        self.filePath = filePath
        self.name = name
        self.center = np.array([0, 0, 0])
        self.load()

    def isSpriteFacingCam(self, cameraPos:np.ndarray = [0, 0, 0]):
        #XX =  points3D[:, 0]
        #YY = -points3D[:, 2]
        #ZZ =  points3D[:, 1]    

        p0, p1, p2, _ = map(np.array, self.points)
        v1 = p1 - p0
        v2 = p2 - p0
        # this needs cleaning in a whole project #TODO
        v1 = np.array([v1[0], -v1[2], v1[1]])
        v2 = np.array([v2[0], -v2[2], v2[1]])

        normal = np.cross(v1, -v2)
        

        viewVector = cameraPos - p0
        dotProduct = np.dot(normal, viewVector)
        return dotProduct < 0 


    def getDistNorm(self, pos:np.ndarray = [0, 0, 0]):
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        dz = pos[2] - self.center[2]
        # no need to calc actual distance, square is fine for comparison
        return dx**2 + dy**2 + dz**2

    def load(self):
        try:
            self.image = cv2.imread(self.filePath)
            xSum = 0
            ySum = 0
            zSum = 0
            for i in range(4):
                xSum += self.points[i][0]
                ySum += self.points[i][1]
                zSum += self.points[i][2]
            xSum /= 4
            ySum /= 4
            zSum /= 4
            self.center = np.array([xSum, ySum, zSum])
        except:
            logger.error("Couldn't load sprite", exc_info=True)
            self.image = np.array([100, 100, 3])




if __name__ == "__main__":
    s = Sprite(np.array([]), "./assets/aruco.png")
    cv2.imshow("images", s.image)
    cv2.waitKey(2000)

