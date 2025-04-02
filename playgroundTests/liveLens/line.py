import numpy as np
from liveLens.threeDeePoint import ThreeDeePoint



class Line:
    def __init__(self, p1: ThreeDeePoint, p2: ThreeDeePoint, name: str = ""):
        self.p1 = p1
        self.p2 = p2
        self.name = name

    def getDistNorm(self, pos:np.ndarray = [0, 0, 0]):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        dz = pos[2] - self.z
        # no need to calc actual distance, square is fine for comparison
        return dx**2 + dy**2 + dz**2

    def __repr__(self):
        return f"x:{self.x}, y:{self.y}, z:{self.z}"
