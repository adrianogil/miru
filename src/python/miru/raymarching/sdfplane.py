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
