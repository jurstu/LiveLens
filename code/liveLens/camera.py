import cv2
import threading
import time
from typing import Callable, Optional

import numpy as np

try:
    import gi

    gi.require_version("Gst", "1.0")
    from gi.repository import Gst
except Exception as exc:  # pragma: no cover
    Gst = None
    _gst_import_error = exc
else:
    _gst_import_error = None
    Gst.init(None)


class Camera:
    def __init__(self, camera_id: [int, str], resolution):
        self.camera_id = camera_id
        self.resolution = resolution
        self.observers: list[Callable[[np.ndarray], None]] = []
        self._stop_event = threading.Event()

        self.latest_frame = self._placeholder_frame()
        self.pipeline: Optional["Gst.Pipeline"] = None
        self.appsink = None
        self._caps_width, self._caps_height = self._width_height()
        self._frame_interval = self._compute_interval()

        self._init_gstreamer()
        self.t = threading.Thread(target=self._run, daemon=True)
        self.t.start()

    def _compute_interval(self) -> float:
        if len(self.resolution) >= 3:
            try:
                fps = float(self.resolution[2])
                if fps > 0:
                    return 1.0 / fps
            except Exception:
                pass
        return 0.0

    def _width_height(self) -> tuple[int, int]:
        width = int(self.resolution[0]) if len(self.resolution) > 0 else 640
        height = int(self.resolution[1]) if len(self.resolution) > 1 else 480
        return width, height

    def _placeholder_frame(self) -> np.ndarray:
        width, height = self._width_height()
        return np.zeros((height, width, 3), dtype=np.uint8)

    def _pipeline_strings(self) -> list[str]:
        width, height = self._width_height()
        fps_clause = ""
        if len(self.resolution) >= 3:
            try:
                fps_val = int(self.resolution[2])
                if fps_val > 0:
                    fps_clause = f",framerate={fps_val}/1"
            except Exception:
                pass

        if isinstance(self.camera_id, int):
            device = f"/dev/video{self.camera_id}"
            return [
                (
                    f"v4l2src device={device} ! "
                    f"image/jpeg,width={width},height={height}{fps_clause} ! "
                    "jpegdec ! videoconvert ! video/x-raw,format=RGB ! "
                    "appsink name=sink emit-signals=true max-buffers=1 drop=true sync=false"
                )
            ]

        base = str(self.camera_id)
        return [
            f"{base} ! jpegdec ! videoconvert ! video/x-raw,format=RGB ! "
            "appsink name=sink emit-signals=true max-buffers=1 drop=true sync=false"
        ]

    def _init_gstreamer(self):
        if Gst is None:
            raise RuntimeError(f"GStreamer not available: {_gst_import_error}")

        for desc in self._pipeline_strings():
            pipeline = Gst.parse_launch(desc)
            sink = pipeline.get_by_name("sink")
            if not sink:
                pipeline.set_state(Gst.State.NULL)
                continue
            pipeline.set_state(Gst.State.PLAYING)
            msg = pipeline.get_bus().timed_pop_filtered(
                2 * Gst.SECOND,
                Gst.MessageType.ERROR | Gst.MessageType.ASYNC_DONE | Gst.MessageType.STATE_CHANGED,
            )
            if msg and msg.type == Gst.MessageType.ERROR:
                pipeline.set_state(Gst.State.NULL)
                continue
            self.pipeline = pipeline
            self.appsink = sink
            return

        raise RuntimeError("Failed to initialize any GStreamer pipeline")

    def _pull_sample(self) -> Optional[np.ndarray]:
        if not self.appsink:
            return None

        sample = self.appsink.emit("try-pull-sample", Gst.SECOND // 2)
        if sample is None:
            return None

        caps = sample.get_caps()
        if caps:
            struct = caps.get_structure(0)
            self._caps_width = struct.get_value("width")
            self._caps_height = struct.get_value("height")

        buf = sample.get_buffer()
        success, map_info = buf.map(Gst.MapFlags.READ)
        if not success:
            return None

        try:
            arr = np.frombuffer(map_info.data, dtype=np.uint8)
            return arr.reshape((self._caps_height, self._caps_width, 3)).copy()
        finally:
            buf.unmap(map_info)

    def _run(self):
        sleep_time = self._frame_interval
        while not self._stop_event.is_set():
            frame = self._pull_sample()
            if frame is not None:
                self.latest_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                if self.observers:
                    self.notify_observers()
            if sleep_time:
                time.sleep(sleep_time)

    def register_observer(self, observer: Callable[[np.ndarray], None]):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer(self.latest_frame)

    def release(self):
        self._stop_event.set()
        if self.t.is_alive():
            self.t.join(timeout=0.2)
        if self.pipeline is not None:
            self.pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    cam = Camera(2, [1280, 720, 30])
    try:
        while True:
            frame = cam.latest_frame
            if frame is None:
                time.sleep(0.01)
                continue

            bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imshow("camera", bgr)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        pass
    finally:
        cam.release()
        cv2.destroyAllWindows()
