import numpy as np
from scipy.spatial.transform import Rotation as R
from loggingSetup import getLogger


logger = getLogger(__name__)

def getExampleK():

    # c2 1280x720
    #return np.array([[5.84802266e+03, 0.00000000e+00, 7.07818118e+02],
    #                 [0.00000000e+00, 5.83163880e+03, 4.29697237e+02],
    #                 [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])


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
        # Y-axis: Points up in the image plane.
        # Z-axis: Points forward (into the camera).
        XX =  points3D[:, 0]
        YY =  points3D[:, 1]
        ZZ =  points3D[:, 2]        
        

        # WTF is this
        x = cameraPos[2]
        y = -cameraPos[1]
        z = cameraPos[0]
        cameraPos = [x, y, z]


        points3D = np.vstack([XX, YY, ZZ]).T
        T = np.array(cameraPos)
        T = T.reshape((3, 1))
        

        # X right
        # Y away
        # Z up
        #so converting from Z points up, X points right, Y points up

        # Yaw is around Y axis, It changes X and Z
        theta = np.radians(yaw)
        #Ry = np.array ([[np.cos(theta), -np.sin(theta), 0],
        #                [np.sin(theta), np.cos(theta), 0],
        #                [0, 0, 1]])
        Ry = np.array ([[ np.cos(theta), 0, np.sin(theta)],
                        [ 0,             1,             0],
                    [    -np.sin(theta), 0, np.cos(theta)]
                    ]
                    )




        # Roll is around X so it changes Y and Z
        theta = np.radians(roll)
        Rr = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta),  np.cos(theta), 0],
            [0,                          0, 1]
        ])
        

        # pitch changes around Z so it changes X and Y
        theta = np.radians(pitch)
        Rp = np.array([
            [1, 0,          0         ],
            [0, np.cos(theta), -np.sin(theta)],
            [0, np.sin(theta),  np.cos(theta)]
        ])

        #R = Rr @ Rp @ Ry
        R = Rp @ Rr @ Ry

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
        #validMask = zCam > 0
        
        #points2DHom = points2DHom[:, validMask]

        # Normalize homogeneous coordinates to get (x, y) image coordinates

        
        points2D = np.divide(points2DHom[:2], points2DHom[2], out=np.zeros_like(points2DHom[:2]), where=abs(points2DHom[2])>0.00001).T.astype(float)
        
        
        return points2D, zCam