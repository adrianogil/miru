import math

from miru.engine.color import Color
from miru.engine.vector import Vector3
from miru.raymarching.sdfbase import SDFObject


class SDFCube(SDFObject):
    def __init__(self, size, color=None):
        super().__init__(color=color)
        self.size = size

    def distance(self, position):
        x = abs(position.x - self.transform.position.x) - self.size.x / 2.0
        y = abs(position.y - self.transform.position.y) - self.size.y / 2.0
        z = abs(position.z - self.transform.position.z) - self.size.z / 2.0

        outside_distance = math.sqrt(
            max(x, 0.0) ** 2
            + max(y, 0.0) ** 2
            + max(z, 0.0) ** 2
        )
        inside_distance = min(max(x, y, z), 0.0)

        return outside_distance + inside_distance

    @staticmethod
    def parse(data):
        cube = SDFCube(Vector3.one())

        if 'size' in data:
            size = data['size']
            cube.size = Vector3(size[0], size[1], size[2])

        if 'transform' in data:
            cube.transform.parse(data['transform'])

        if 'color' in data:
            color = data['color']
            cube.color = Color(color[0], color[1], color[2], color[3])

        return cube
