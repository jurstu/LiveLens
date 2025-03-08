import numpy as np
from scipy.spatial.transform import Rotation as R


class PinholeCamera:
    def __init__(self, K: np.ndarray):
        self.K = K

    def getProjections(self, points3D: np.ndarray, roll: float, pitch: float, yaw: float, cameraPos: np.ndarray):
        r = R.from_euler('xyz', [roll, pitch, yaw], degrees=True).as_matrix()
        t = -np.dot(r, cameraPos)

        # 3x4 Extrinsic matrix [R | t]
        extrinsicMatrix = np.hstack((r, t.reshape(3, 1)))

        # get homogeneous world position coordinates
        worldPointsHomogeneous = np.hstack((points3D, np.ones((points3D.shape[0], 1))))

        cameraCoords = extrinsicMatrix @ worldPointsHomogeneous.T
        zCam = cameraCoords[2, :]
        
        # only extract points in front of the camera
        #validMask = zCam > 0
        #cameraCoords = cameraCoords[:, validMask]

        if cameraCoords.shape[1] == 0:
            return np.empty((0, 2))

        image_coords = self.K @ cameraCoords[:3, :]
        image_coords /= image_coords[2, :]

        return image_coords[:2, :].T
    
