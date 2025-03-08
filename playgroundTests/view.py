import cv2
import numpy as np

class DrawingCanvas:
    def __init__(self, width=800, height=600, bgColor=(255, 255, 255)):
        self.width = width
        self.height = height
        self.bgColor = bgColor
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.canvas[:] = np.array(self.bgColor, dtype=np.uint8)

        self.drawing = False




if __name__ == "__main__":
    canvas = DrawingCanvas()

    while True:
        cv2.imshow("main view", canvas.canvas)
        if cv2.waitKey(1) & 0xFF == 27:  # Press 'ESC' to exit
            break

    cv2.destroyAllWindows()