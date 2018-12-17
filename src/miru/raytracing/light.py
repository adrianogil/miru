from miru.engine.transform import Transform
from miru.engine.vector import Vector3


class Light:
    def __init__(self, color, intensity=1.0):
        self.color = color
        self.intensity = intensity
        self.transform = Transform()

