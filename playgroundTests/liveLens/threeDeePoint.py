import numpy as np

class ThreeDeePoint:
    def __init__(self, x: float, y: float, z: float, color:np.ndarray=[0, 0, 0], name: str = ""):
        self.x = x
        self.y = y
        self.z = z
        self.name = name

    def __add__(self, other):
        return ThreeDeePoint(self.x + other.x, 
                             self.y + other.y, 
                             self.z + other.z, 
                             "sum of " + self.name + " and " + other.name)

    def __truediv__(self, other):
        if(type(other) == int or type(other) == float):
            return ThreeDeePoint(self.x/other, 
                                 self.y/other, 
                                 self.z/other, 
                                 self.name + " divided by " + str(other))

    def getDistNorm(self, pos:np.ndarray = [0, 0, 0]):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        dz = pos[2] - self.z
        # no need to calc actual distance, square is fine for comparison
        return dx**2 + dy**2 + dz**2

    def __repr__(self):
        return f"x:{self.x}, y:{self.y}, z:{self.z}"