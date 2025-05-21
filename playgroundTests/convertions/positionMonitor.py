import numpy as np





class PositionMonitor:
    def __init__(self):
        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.isPosValid = 0
        self.wgsPositions = [[52.22604175647743, 20.929888710983388, 0],
                            [52.22604175647743, 20.929888710983388, 1]
                            ]


    # in the future this abstraction layer could be used to apply Kalmann filtering
    def setCameraPosition(self, lat:float, lon:float, alt:float):
        self.isPosValid = 1
        self.lat = lat
        self.lon = lon
        self.alt = alt
        latr = np.radians(self.lat)
        lonr = np.radians(self.lon)
        # saving rotation matrix for all future transformation, since it's modified only during 
        # setting of reference position (lat, lon, alt)
        self.R = np.array([
            [-np.sin(lonr),             np.cos(lonr),              0],
            [-np.sin(latr)*np.cos(lonr), -np.sin(latr)*np.sin(lonr), np.cos(latr)],
            [np.cos(latr)*np.cos(lonr),  np.cos(latr)*np.sin(lonr),  np.sin(latr)]
        ]) 
        self.ref_ecef = self.wgs84ToEcef(lat, lon, alt)


    def getPositionsInENU(self):
        output = []
        for pos in self.wgsPositions:
            enu = self.wgs84ToEnuFromCamera(pos[0] + 1, pos[1] + 2, pos[2])
            output.append(enu)
        return output

    def wgs84ToEcef(self, lat:float, lon:float, alt:float):
        a = 6378137.0  # semi-major axis (meters)
        e2 = 6.69437999014e-3  # eccentricity squared

        latr = np.radians(lat)
        lonr = np.radians(lon)

        N = a / np.sqrt(1 - e2 * np.sin(latr)**2)

        x = (N + alt) * np.cos(latr) * np.cos(lonr)
        y = (N + alt) * np.cos(latr) * np.sin(lonr)
        z = ((1 - e2) * N + alt) * np.sin(latr)
        return np.array([x, y, z])

    def wgs84ToEnuFromCamera(self, lat:float, lon:float, alt:float):
        ecef = self.wgs84ToEcef(lat, lon, alt)
        dx = ecef - self.ref_ecef
        return self.R @ dx






if __name__ == "__main__":
    lat1, lon1 = 52.149306, 20.981002
    lat2, lon2 = 52.178684, 20.955339

    pm = PositionMonitor()
    pm.setCameraPosition(lat1, lon1, 0)
    enuEndOfRunway = pm.wgs84ToEnuFromCamera(lat2, lon2, 0)
    print(enuEndOfRunway)

    exit()
