import numpy as np
from scipy.spatial.transform import Rotation as R
from loggingSetup import getLogger


logger = getLogger(__name__)

def getExampleK():
    # 1280x720 camera
    return np.array([[800,   0, 640],
                    [   0, 800, 360],
                    [   0,   0,   1]])



class PinholeCamera:
    def __init__(self, K):
        self.K = K

    def getProjections(self, points3D: np.ndarray, roll: float, pitch: float, yaw:float, cameraPos: np.ndarray):
        # later in projection it goes like this
        # X-axis: Points to the right in the image plane.
        # Y-axis: Points downward in the image plane.
        # Z-axis: Points forward (into the scene, away from the camera).
        XX =  points3D[:, 0]
        YY = -points3D[:, 2]
        ZZ =  points3D[:, 1]        
        ## so converting from Z points up, X points right, Y points up is basically this
        
        x = cameraPos[1]
        y = -cameraPos[2]
        z = -cameraPos[0]
        cameraPos = [x, y, z]


        points3D = np.vstack([XX, YY, ZZ]).T
        T = np.array(cameraPos)
        T = T.reshape((3, 1))
        

        # Y
        theta = np.radians(-90-yaw)
        Ry = np.array([[np.cos(theta), 0, np.sin(theta)],
                    [0, 1, 0],
                    [-np.sin(theta), 0, np.cos(theta)]])
        

        # Z 
        theta = np.radians(roll)
        Rr = np.array ([[np.cos(theta), -np.sin(theta), 0],
                        [np.sin(theta), np.cos(theta), 0],
                        [0, 0, 1]])

        # X
        theta = np.radians(pitch)
        Rp = np.array([
            [1, 0,          0         ],
            [0, np.cos(theta), -np.sin(theta)],
            [0, np.sin(theta),  np.cos(theta)]
        ])

        R = Rr @ Rp @ Ry

        # not sure if this should be here
        T = -np.dot(R, T)

        # Compute the projection matrix: P = K [R | T]
        
        P = self.K @ np.hstack((R, T))
        
        # Convert 3D points to homogeneous coordinates (add 1 as the fourth row)
        points3DHom = np.hstack((points3D, np.ones((points3D.shape[0], 1))))
        
        # Project points: 2D homogeneous coordinates
        points2DHom = P @ points3DHom.T
        zCam = points2DHom[2, :]

        # only extract points in front of the camera
        validMask = zCam > 0
        
        points2DHom = points2DHom[:, validMask]

        # Normalize homogeneous coordinates to get (x, y) image coordinates
        points2D = (points2DHom[:2] / points2DHom[2]).T.astype(int)
        
        return points2D
    



#class PinholeCamera:
#    def __init__(self, K: np.ndarray):
#        self.K = K
#
#    def getProjections(self, points3D: np.ndarray, roll: float, pitch: float, yaw: float, cameraPos: np.ndarray):
#        r = R.from_euler('xyz', [roll, pitch, yaw], degrees=True).as_matrix()
#        t = -np.dot(r, np.array([cameraPos]).T)
#        #t = np.array([cameraPos]).T
#        P = self.K @ np.hstack((r, t))
#        worldPointsHomogeneous = np.hstack((points3D, np.ones((points3D.shape[0], 1))))
#        imageCoords = P @ worldPointsHomogeneous.T
#        imageCoords = (imageCoords[:2] / imageCoords[2]).T.astype(int)
#        return imageCoords
#
#
#        # 3x4 Extrinsic matrix [R | t]
#        extrinsicMatrix = np.hstack((r, t.reshape(3, 1)))
#
#        # get homogeneous world position coordinates
#        worldPointsHomogeneous = np.hstack((points3D, np.ones((points3D.shape[0], 1))))
#
#        cameraCoords = extrinsicMatrix @ worldPointsHomogeneous.T
#        zCam = cameraCoords[2, :]
#        
#        # only extract points in front of the camera
#        #validMask = zCam > 0
#        #cameraCoords = cameraCoords[:, validMask]
#
#        # TODO add calculating if v, u are in the camera frame
#
#        if cameraCoords.shape[1] == 0:
#            return np.empty((0, 2))
#
#        image_coords = self.K @ cameraCoords[:3, :]
#        image_coords /= image_coords[2, :]
#
#        return image_coords[:2, :].T
    
