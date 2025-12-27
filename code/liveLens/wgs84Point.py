import numpy as np
from .threeDeePoint import ThreeDeePoint

class Wgs84Point:
    def __init__(self, lat, lon, alt):
        self.lat = lat
        self.lon = lon
        self.alt = alt


    def getMyENU(self, lat0, lon0, alt0):
        x0, y0, z0 = self.getEcef(lat0, lon0, alt0)
        x, y, z = self.getEcef(self.lat, self.lon, self.alt)

        dx = x - x0
        dy = y - y0
        dz = z - z0

        lat0 = np.deg2rad(lat0)
        lon0 = np.deg2rad(lon0)

        sin_lat = np.sin(lat0)
        cos_lat = np.cos(lat0)
        sin_lon = np.sin(lon0)
        cos_lon = np.cos(lon0)

        # Rotation matrix
        R = np.array([
            [-sin_lon,            cos_lon,           0],
            [-sin_lat*cos_lon, -sin_lat*sin_lon, cos_lat],
            [ cos_lat*cos_lon,  cos_lat*sin_lon, sin_lat]
        ])
        enu = R @ np.array([dx, dy, dz])
        # ENU
        # NUE
        # 
        # NED 
        # NUW North, Up, West
        
        tdp = ThreeDeePoint(enu[1], enu[2], -enu[0])
        return tdp



    def getEcef(self, lat, lon, h):
        
        a = 6378137.0                  # semi-major axis (meters)
        f = 1 / 298.257223563
        e2 = f * (2 - f)               # first eccentricity squared

        lat = np.deg2rad(lat)
        lon = np.deg2rad(lon)

        sin_lat = np.sin(lat)
        cos_lat = np.cos(lat)
        sin_lon = np.sin(lon)
        cos_lon = np.cos(lon)

        N = a / np.sqrt(1 - e2 * sin_lat**2)

        x = (N + h) * cos_lat * cos_lon
        y = (N + h) * cos_lat * sin_lon
        z = (N * (1 - e2) + h) * sin_lat

        return np.array([x, y, z])




