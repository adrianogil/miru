from miru.engine.vector import Vector3
from miru.raymarching.sdfbase import SDFObject


class SDFPlane(SDFObject):
    """Infinite plane defined by dot(point, normal) = offset."""

    def __init__(self, normal=None, offset=0.0, color=None):
        if normal is None:
            normal = Vector3.up()

        if normal.magnitude() == 0.0:
            raise ValueError("Plane normal must not be the zero vector")

        super().__init__(color=color)
        self.normal = normal.normalized()
        self.offset = float(offset)

    def distance(self, position):
        local_position = position.minus(self.transform.position)
        return local_position.dot_product(self.normal) - self.offset

    @staticmethod
    def parse(data):
        normal_data = data.get("normal", [0.0, 1.0, 0.0])
        plane = SDFPlane(
            Vector3(normal_data[0], normal_data[1], normal_data[2]),
            offset=float(data.get("offset", 0.0)),
        )
        if "transform" in data:
            plane.transform.parse(data["transform"])
        return plane
