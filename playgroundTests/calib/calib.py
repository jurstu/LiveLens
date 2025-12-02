import cv2
import numpy as np
import glob

# === USER SETTINGS ===
squares_x = 5   # number of chessboard squares in X direction
squares_y = 7   # number of chessboard squares in Y direction
square_length = 30.0   # mm - real size of a ChArUco square
marker_length = 20.0   # mm - real size of an ArUco marker

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
board = cv2.aruco.CharucoBoard((squares_x, squares_y), square_length, marker_length, dictionary)

all_corners = []
all_ids = []
image_size = None

# Load images
images = glob.glob("/home/jur/calibImages/*.jpg")

for fname in images:
    print("Processing:", fname)

    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect ArUco markers
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary)

    if len(corners) > 0:
        # Refine marker detection
        cv2.aruco.refineDetectedMarkers(gray, board, corners, ids, rejected)

        # Interpolate Charuco corners
        retval, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(
            markerCorners=corners,
            markerIds=ids,
            image=gray,
            board=board
        )

        if retval > 4:  # need at least some valid corners
            all_corners.append(charuco_corners)
            all_ids.append(charuco_ids)

            # Draw for visualization
            cv2.aruco.drawDetectedCornersCharuco(img, charuco_corners, charuco_ids)
            cv2.imshow("ChArUco Detection", img)
            cv2.waitKey(200)

            if image_size is None:
                image_size = gray.shape[::-1]

cv2.destroyAllWindows()

# === Camera Calibration ===
retval, K, dist, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
    charucoCorners=all_corners,
    charucoIds=all_ids,
    board=board,
    imageSize=image_size,
    cameraMatrix=None,
    distCoeffs=None
)

print("\n=== RESULTS ===")
print("\nCamera matrix K:\n", K)
print("\nDistortion coefficients:\n", dist)

for i, (r, t) in enumerate(zip(rvecs, tvecs)):
    R, _ = cv2.Rodrigues(r)
    print(f"\nImage {i} extrinsics:")
    print("Rotation matrix:\n", R)
    print("Translation vector (mm):\n", t)
