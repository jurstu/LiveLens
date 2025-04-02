import numpy as np
from liveLens.threeDeePoint import ThreeDeePoint



class Line:
    def __init__(self, p1: ThreeDeePoint, p2: ThreeDeePoint, name: str = ""):
        self.p1 = p1
        self.p2 = p2
        self.name = name

    def getDistNorm(self, pos:np.ndarray = [0, 0, 0]):

        centerPoint = (self.p1 + self.p2)/2

        dx = pos[0] - centerPoint.x
        dy = pos[1] - centerPoint.y
        dz = pos[2] - centerPoint.z
        # no need to calc actual distance, square is fine for comparison
        return dx**2 + dy**2 + dz**2

    def __repr__(self):
        return f"line: p1: {self.p1}, p2: {self.p2}"
