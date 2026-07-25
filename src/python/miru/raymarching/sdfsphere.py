from miru.engine.color import Color
from miru.raymarching.sdfbase import SDFObject


class SDFSphere(SDFObject):
    def __init__(self, radius, color=None):
        if radius <= 0.0:
            raise ValueError("Sphere radius must be positive")

        super().__init__(color=color)
        self.radius = float(radius)

    def distance(self, position):
        return position.minus(self.transform.position).magnitude() - self.radius

    @staticmethod
    def parse(data):
        sphere = SDFSphere(float(data.get("radius", 1.0)))

        if "transform" in data:
            sphere.transform.parse(data["transform"])

        if "color" in data:
            color = data["color"]
            sphere.color = Color(color[0], color[1], color[2], color[3])

        return sphere
