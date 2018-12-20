from miru.engine.transform import Transform
from miru.engine.color import Color

from miru.engine.vector import Vector3
from miru.engine.material import Material

class SDFUtils:

    @staticmethod
    # Using the gradient of the SDF, estimate the normal on
    # the surface at point p.
    def get_normal(distance_method, current_pos):
        eps = 0.01

        eps_x = Vector3(eps, 0.0, 0.0)
        normal_x = distance_method(current_pos.add(eps_x))
        normal_x = normal_x - distance_method(current_pos.minus(eps_x))

        eps_y = Vector3(0.0, eps, 0.0)
        normal_y = distance_method(current_pos.add(eps_y))
        normal_y = normal_y - distance_method(current_pos.minus(eps_y))

        eps_z = Vector3(0.0, 0.0, eps)
        normal_z = distance_method(current_pos.add(eps_z))
        normal_z = normal_z - distance_method(current_pos.minus(eps_z))

        return Vector3(normal_x, normal_y, normal_z).normalized()


class SDFCube:
    def __init__(self, size):
        self.size = size
        self.transform = Transform()
        self.color = Color.random()
        self.material = Material.default()

    def pre_render(self):
        self.transform.update_internals()

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
        interception['normal'] = SDFUtils.get_normal(self.distance, interception['hit_point'])

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
        self.transform.update_internals()

    def distance(self, position):
        return position.minus(self.transform.position).magnitude() - self.radius

    def render(self, scene, interception):
        interception['normal'] = interception['hit_point'].minus(self.transform.position).normalized()

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
