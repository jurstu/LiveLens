import math
from dataclasses import dataclass


@dataclass
class CameraIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    distortion: tuple[float, ...] = ()


@dataclass
class CameraExtrinsics:
    x: float = 0
    y: float = 0
    z: float = 0
    roll: float = 0
    pitch: float = 0
    yaw: float = 0


class LiveLensCamera:
    def __init__(
        self,
        resolution=(640, 480, 30),
        intrinsics=None,
        extrinsics=None,
        name="",
    ):
        self.resolution = resolution
        self.width = resolution[0]
        self.height = resolution[1]
        self.fps = resolution[2] if len(resolution) > 2 else None

        self.name = name
        self.uses_default_intrinsics = intrinsics is None
        self.intrinsics = intrinsics or self._default_fpv_intrinsics()
        self.extrinsics = extrinsics or CameraExtrinsics()

    def set_resolution(self, resolution):
        self.resolution = resolution
        self.width = resolution[0]
        self.height = resolution[1]
        self.fps = resolution[2] if len(resolution) > 2 else None
        if self.uses_default_intrinsics:
            self.intrinsics = self._default_fpv_intrinsics()

    def set_intrinsics(self, fx, fy, cx, cy, distortion=()):
        self.uses_default_intrinsics = False
        self.intrinsics = CameraIntrinsics(fx, fy, cx, cy, tuple(distortion))

    def set_extrinsics(self, x=0, y=0, z=0, roll=0, pitch=0, yaw=0):
        self.extrinsics = CameraExtrinsics(x, y, z, roll, pitch, yaw)

    def get_intrinsics(self):
        return self.intrinsics

    def get_extrinsics(self):
        return self.extrinsics

    def get_resolution(self):
        return self.resolution

    def _default_fpv_intrinsics(self):
        horizontal_fov = math.radians(120)
        focal_length = self.width / (2 * math.tan(horizontal_fov / 2))
        return CameraIntrinsics(
            fx=focal_length,
            fy=focal_length,
            cx=self.width / 2,
            cy=self.height / 2,
        )
