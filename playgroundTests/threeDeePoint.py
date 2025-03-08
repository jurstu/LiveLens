import numpy as np




class ThreeDeePoint:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class ThreeDeePointWgs84:
    def __init__(self, lat: float, lon: float, height: float):
        self.lat = lat
        self.lon = lon
        self.height = height

