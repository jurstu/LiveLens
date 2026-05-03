from dataclasses import dataclass


@dataclass
class WorldPoint:
    x: float
    y: float
    z: float
    color: tuple[int, int, int, int] = (0, 255, 0, 255)
    name: str = ""
    visible: bool = True


@dataclass
class WorldLine:
    p1: WorldPoint
    p2: WorldPoint
    color: tuple[int, int, int, int] = (0, 255, 0, 255)
    name: str = ""
    visible: bool = True


@dataclass
class WorldSphere:
    x: float
    y: float
    z: float
    radius: float
    color: tuple[int, int, int, int] = (0, 255, 0, 255)
    name: str = ""
    visible: bool = True


@dataclass
class WorldGlyph:
    x: float
    y: float
    z: float
    text: str
    color: tuple[int, int, int, int] = (0, 255, 0, 255)
    name: str = ""
    visible: bool = True


@dataclass
class WorldStl:
    path: str
    x: float = 0
    y: float = 0
    z: float = 0
    roll: float = 0
    pitch: float = 0
    yaw: float = 0
    scale: float = 1
    color: tuple[int, int, int, int] = (0, 255, 0, 255)
    name: str = ""
    visible: bool = True


class LiveLensWorld:
    def __init__(self):
        self.points = []
        self.lines = []
        self.spheres = []
        self.glyphs = []
        self.stls = []

    def add_point(self, x, y, z, color=(0, 255, 0, 255), name="", visible=True):
        point = WorldPoint(x, y, z, color, name, visible)
        self.points.append(point)
        return point

    def add_line(self, p1, p2, color=(0, 255, 0, 255), name="", visible=True):
        line = WorldLine(p1, p2, color, name, visible)
        self.lines.append(line)
        return line

    def add_sphere(self, x, y, z, radius, color=(0, 255, 0, 255), name="", visible=True):
        sphere = WorldSphere(x, y, z, radius, color, name, visible)
        self.spheres.append(sphere)
        return sphere

    def add_glyph(self, x, y, z, text, color=(0, 255, 0, 255), name="", visible=True):
        glyph = WorldGlyph(x, y, z, text, color, name, visible)
        self.glyphs.append(glyph)
        return glyph

    def add_stl(
        self,
        path,
        x=0,
        y=0,
        z=0,
        roll=0,
        pitch=0,
        yaw=0,
        scale=1,
        color=(0, 255, 0, 255),
        name="",
        visible=True,
    ):
        stl = WorldStl(path, x, y, z, roll, pitch, yaw, scale, color, name, visible)
        self.stls.append(stl)
        return stl

    def clear(self):
        self.points.clear()
        self.lines.clear()
        self.spheres.clear()
        self.glyphs.clear()
        self.stls.clear()

    def get_renderables(self):
        return {
            "points": self.points,
            "lines": self.lines,
            "spheres": self.spheres,
            "glyphs": self.glyphs,
            "stls": self.stls,
        }
