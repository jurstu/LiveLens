import cv2
import cv2.text
import numpy as np
from pinholeCamera import PinholeCamera, getExampleK
from worldStore import WorldStore
from view import View
from loggingSetup import getLogger

import imageio

logger = getLogger(__name__)


class GifGenerator:
    def __init__(self, frames=np.ndarray, dt: int = 0.1, outputSize:np.ndarray = np.array([360,240])):
        self.frames = frames
        self.dt = dt
        self.outputSize = outputSize
        

    def write(self, gifName, loop=2048):
        for frame in self.frames:
            frame = cv2.resize(frame, self.outputSize)

        imageio.mimsave(gifName, self.frames, fps=1/self.dt, loop=loop)






if __name__ == "__main__":
    view = View()
    view.worldStore.generateFloor(np.array([0, 0, 0]), 3, 0.05)
    R = 1
    position = [-R, 0, 0.1]
    view.setCameraPosAtt(position, 0, 0, 0)
    angle = 0

    frames = []
    while angle < 360:
        angle += 5
        cv2.imshow("main view", view.canvas)
        position = [-R * np.cos(np.deg2rad(angle)), R * np.sin(np.deg2rad(angle)), 0.3]
        view.setCameraPosAtt(position, 0, 0, angle + 90)
        view.drawWorld()
        frames.append(view.canvas)
        if cv2.waitKey(33) & 0xFF == 27:  # Press 'ESC' to exit
            break

    cv2.destroyAllWindows()

    gg = GifGenerator(frames, dt=0.033)
    gg.write("../.github/static/animation.gif")



