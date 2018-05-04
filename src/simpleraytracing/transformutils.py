import numpy as np

def getTranslationMatrix(T):
    '''
        getTranslationMatrix(T)
            T : 3-sized vector
    '''
    return np.array(
             [[1, 0, 0, T.x],
              [0, 1, 0, T.y],
              [0, 0, 1, T.z],
              [0, 0, 0, 1]]
              )

def getOrientationMatrix(eulerRotation):
   m = getOrientationMatrixZ(eulerRotation.z)
   m = m.dot(getOrientationMatrixX(eulerRotation.x))
   m = m.dot(getOrientationMatrixY(eulerRotation.y))

   return m

def getOrientationMatrixX(theta):
    theta = theta * np.pi / 180
    return np.array(
             [[1, 0, 0, 0],
              [0, np.cos(theta), -np.sin(theta), 0],
              [0, np.sin(theta), np.cos(theta), 0],
              [0, 0, 0, 1]]
              )

def getOrientationMatrixY(theta):
    theta = theta * np.pi / 180
    return np.array(
             [[np.cos(theta), 0, np.sin(theta), 0],
              [0, 1, 0, 0],
              [-np.sin(theta), 0, np.cos(theta), 0],
              [0, 0, 0, 1]]
              )

def getOrientationMatrixZ(theta):
    theta = theta * np.pi / 180
    return np.array(
             [[np.cos(theta), -np.sin(theta), 0, 0],
              [np.sin(theta), np.cos(theta), 0, 0],
              [0, 0, 1, 0],
              [0, 0, 0, 1]]
              )

def getScalingMatrix(s):
    return np.array(
             [[s.x, 0, 0, 0],
              [0, s.y, 0, 0],
              [0, 0, s.z, 0],
              [0, 0, 0, 1]]
              )

def getScalingMatrixFrom(s, v1, v2, v3):
    F = np.array(
             [[v1.x, v2.x, v3.x, 0],
              [v1.y, v2.y, v3.y, 0],
              [v1.z, v2.z, v3.z, 0],
              [   0,    0,    0, 1]]
              )
    return np.dot(np.dot(F,getScalingMatrix(s)),np.transpose(F))