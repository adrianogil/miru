class Camera:
    
    ORTOGRAPHIC=1
    PERSPECTIVE=2
    
    def __init__(self):
        self.mode = Camera.PERSPECTIVE
        self.fov = 60