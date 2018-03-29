from vector import Vector3

class Transform:
    def __init__(self):
        self.position = Vector3(0,0,0)
        self.forward = Vector3(0,0,1)
        self.right = Vector3(1,0,0)
        self.left = Vector3(-1,0,0)
        self.up = Vector3(0,1,0)