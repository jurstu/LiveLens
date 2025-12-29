from .wgs84Point import Wgs84Point


class Wgs84World:
    def __init__(self):
        self.points = [
            Wgs84Point(52.201589, 21.045718, 0),
            Wgs84Point(52.201761, 21.045724, 0),
            Wgs84Point(52.201761, 21.045724, 100),
            Wgs84Point(52.201589, 21.045718, 100),


            Wgs84Point(52.201558, 21.038555, 3), # 4 punkty na szatni
            Wgs84Point(52.201561, 21.038594, 3),
            Wgs84Point(52.201445, 21.038559, 3),
            Wgs84Point(52.201445, 21.038600, 3),
        ]

    def getPoints(self, lat, lon, alt):
        output = []
        for p in self.points:
            pp = p.getMyENU(lat, lon, alt)
            output.append(pp)

        return output


