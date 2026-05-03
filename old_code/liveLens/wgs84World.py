from .wgs84Point import Wgs84Point


class Wgs84World:
    def __init__(self):
        self.points = [
            Wgs84Point(52.201589, 21.045718, 100),
            Wgs84Point(52.201761, 21.045724, 100),
            Wgs84Point(52.201761, 21.045724, 160),
            Wgs84Point(52.201589, 21.045718, 160),


            Wgs84Point(52.201558, 21.038555, 100), # 4 punkty na szatni
            Wgs84Point(52.201561, 21.038594, 100),
            Wgs84Point(52.201445, 21.038559, 100),
            Wgs84Point(52.201445, 21.038600, 100),
        ]

    def getPoints(self, lat, lon, alt):
        output = []
        for p in self.points:
            pp = p.getMyENU(lat, lon, alt)
            output.append(pp)

        return output


