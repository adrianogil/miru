from miru.engine.transform import Transform

class Camera:
    
    ORTOGRAPHIC=1
    PERSPECTIVE=2
    
    def __init__(self):
        self.mode = Camera.PERSPECTIVE
        self.fov = 60

        self.near = 0.01
        self.far = 1000

        self.transform = Transform()