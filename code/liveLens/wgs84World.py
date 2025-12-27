from .wgs84Point import Wgs84Point


class Wgs84World:
    def __init__(self):
        self.points = [
            Wgs84Point(52.201589, 21.045718, 0),
            Wgs84Point(52.201761, 21.045724, 0),
            Wgs84Point(52.201761, 21.045724, 100),
            Wgs84Point(52.201589, 21.045718, 100)
        ]

    def getPoints(self, lat, lon, alt):
        output = []
        for p in self.points:
            pp = p.getMyENU(lat, lon, alt)
            output.append(pp)

        return output


