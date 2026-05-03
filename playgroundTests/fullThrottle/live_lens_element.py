import numpy as np

try:
    from .live_lens_camera import LiveLensCamera
    from .live_lens_pyrenderer import LiveLensPyrenderer
    from .live_lens_world import LiveLensWorld
except Exception:
    from live_lens_camera import LiveLensCamera
    from live_lens_pyrenderer import LiveLensPyrenderer
    from live_lens_world import LiveLensWorld

try:
    from local_signals import Signal
except Exception:
    class Signal:
        def __init__(self, name=""):
            self.name = name
            self.receivers = []

        def add_receiver(self, call):
            self.receivers.append(call)

        def trigger(self, value=None):
            for receiver in self.receivers:
                if value is None:
                    receiver()
                else:
                    receiver(value)


class LiveLensElement:
    def __init__(
        self,
        resolution=(640, 480, 30),
        camera_intrinsics=None,
        camera_extrinsics=None,
    ):
        self.camera = LiveLensCamera(
            resolution=resolution,
            intrinsics=camera_intrinsics,
            extrinsics=camera_extrinsics,
        )
        self.world = LiveLensWorld()
        self.renderer = LiveLensPyrenderer(self.camera)

        self.x = 0
        self.y = 0
        self.z = 0
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.new_frame_signal = Signal("new live lens overlay frame")

    def update_data(self, data):

        x = data.get("x", 0)
        y = data.get("y", 0)
        z = data.get("z", 0)
        roll = data.get("roll", 0)
        pitch = data.get("pitch", 0)
        yaw = data.get("yaw", 0)

        self.x = x
        self.y = y
        self.z = z
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

        self.generate_overlay_frame()

    def get_data(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "roll": self.roll,
            "pitch": self.pitch,
            "yaw": self.yaw,
        }

    def generate_world(self, fill_world, start_x=0, start_y=0, start_z=0):
        self.world.clear()
        fill_world(self.world, start_x, start_y, start_z)
        return self.world

    def generate_overlay_frame(self):
        overlay = self.renderer.generate_overlay_frame(self.world)
        self.new_frame_signal.trigger(overlay)
        return overlay



if __name__ == "__main__":
    import math

    import cv2
    import imageio

    from live_lens_world_generators import generate_axis_world

    lle = LiveLensElement(resolution=(640, 480, 30))
    lle.generate_world(generate_axis_world)

    frames = []
    frame = None
    radius = 4
    height = 2
    frame_count = 120

    for i in range(frame_count):
        angle = 2 * math.pi * i / frame_count
        x = math.cos(angle) * radius
        z = math.sin(angle) * radius
        pitch = -math.degrees(math.atan2(height, radius))
        yaw = math.degrees(angle) + 90

        lle.camera.set_extrinsics(x=x, y=height, z=z, pitch=pitch, yaw=yaw)
        frame = lle.generate_overlay_frame()
        frames.append(frame)

    if frame is not None:
        cv2.imwrite("output.png", cv2.cvtColor(frame, cv2.COLOR_RGBA2BGRA))
        imageio.mimsave("output.gif", frames, duration=1 / 30)

    lle.renderer.close()
