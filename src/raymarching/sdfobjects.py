from engine.transform import Transform
from engine.color import Color

from engine.vector import Vector3
from engine.material import Material

class SDFCube:
    def __init__(self, size):
        self.size = size
        self.transform = Transform()
        self.color = Color.random()
        self.material = Material.default()

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

    def render(self, scene, interception):
        if self.material is not None:
            return self.material.render(scene, interception)

        print('cube has no material')

        return self.albedo

    @staticmethod
    def parse(data):
        # print('parsing data ' + str(data))
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


class SDFSphere:
    def __init__(self, radius):
        self.radius = radius
        self.transform = Transform()
        self.albedo = Color.random()
        self.material = Material.default()

    def pre_render(self):
        pass

    def distance(self, position):
        return position.minus(self.transform.position).magnitude() - self.radius

    def render(self, scene, interception):
        if self.material is not None:
            return self.material.render(scene, interception)

        print('sphere has no material')

        return self.albedo

    @staticmethod
    def parse(data):
        # print('parsing data ' + str(data))
        sphere = SDFSphere(1.0)

        if 'radius' in data:
            sphere.radius = float(data['radius'])

        if 'transform' in data:
            sphere.transform.parse(data['transform'])

        return sphere
