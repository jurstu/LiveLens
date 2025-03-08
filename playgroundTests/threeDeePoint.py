import numpy as np




class ThreeDeePoint:
    def __init__(self, x: float, y: float, z: float, name: str = ""):
        self.x = x
        self.y = y
        self.z = z
        self.name = name

    def __repr__(self):
        return f"x:{self.x}, y:{self.y}, z:{self.z}"

class ThreeDeePointWgs84:
    def __init__(self, lat: float, lon: float, height: float, name: str = ""):
        self.lat = lat
        self.lon = lon
        self.height = height

