import cv2
import numpy as np

# Parameters
squares_x = 5
squares_y = 7
square_length = 30  # mm
marker_length = 20  # mm

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
board = cv2.aruco.CharucoBoard((squares_x, squares_y), square_length, marker_length, dictionary)

img = board.generateImage((1200, 1600))
cv2.imwrite("charuco_board.png", img)
print("Saved charuco_board.png")
