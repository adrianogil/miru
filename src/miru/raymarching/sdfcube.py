from miru.engine.transform import Transform
from miru.engine.color import Color

from miru.engine.vector import Vector3


class SDFCube:
    def __init__(self, size):
        self.size = size
        self.transform = Transform()
        self.color = Color.random()

    def pre_render(self):
        pass

    def distance(self, position):

        x = max(
            position.x - self.transform.position.x - self.size.x / 2.0,
            self.transform.position.x - position.x - self.size.x / 2.0
            )

        y = max(
            position.y - self.transform.position.y - self.size.y / 2.0,
            self.transform.position.y - position.y - self.size.y / 2.0
            )

        z = max(
            position.z - self.transform.position.z - self.size.z / 2.0,
            self.transform.position.z - position.z - self.size.z / 2.0
            )

        d = max(x, y)
        d = max(d, z)

        # print("SDFCube - distance - " + str(position) + " - " + str(d))

        return d

    def render(self, scene, position):
        return self.color;

    @staticmethod
    def parse(data):
        # print('parsing data ' + str(data))
        cube = None

        if 'size' in data:
            size = data['size']
            cube = SDFCube(Vector3(size[0], size[1], size[2]))

            if 'transform' in data:
                cube.transform.parse(data['transform'])

            if 'color' in data:
                color = data['color']
                cube.color = Color(color[0], color[1], color[2], color[3])

        return cube
