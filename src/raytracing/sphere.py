from engine.transform import Transform
from engine.vector import Vector3,Vector2
from engine.color import Color

from engine.material import Material

import numpy as np

class Sphere:
    def __init__(self, radius):
        self.radius = radius

        self.albedo = Color(1.0, 0.0, 0.0, 1.0)

        self.transform = Transform()

        self.material = Material.default()

    def pre_render(self):
        self.transform.update_internals()

    def set_material(self, material):
        self.material = material

    def render(self, scene, interception):
        if self.material != None:
            return self.material.render(scene, interception)

        print('sphere has no material')

        return self.albedo


    def intercepts(self, ray):
        # geometric solution
        # https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-sphere-intersection

        # print('Sphere intercepts ray ' + str(ray))

        radius2 = self.radius * self.radius

        L = self.transform.position.minus(ray.origin)
        tca = L.dot_product(ray.direction)

        d2 = L.dot_product(L) - tca * tca
        if d2 > radius2:
            return {'result': False, 'hit_point': Vector3.zero, 'normal' : None, 'uv' : Vector2.zero}
        thc = np.sqrt(radius2 - d2)
        t0 = tca - thc
        t1 = tca + thc

        if t0 > t1:
            tmp = t1
            t1 = t0
            t0 = tmp

        if t0 < 0:
            t0 = t1 # if t0 is negative, let's use t1 instead
            if t0 < 0:
                return {'result': False, 'hit_point': Vector3.zero, 'normal' : None, 'uv' : Vector2.zero} # both t0 and t1 are negative
        t = t0;

        hit_point = ray.origin.add(ray.direction.multiply(t))
        normal = hit_point.minus(self.transform.position).normalized()

        v = normal

        v = self.transform.apply_transform_to_direction(v)

        try:
            longlat = Vector2(np.arctan2(v.x, v.z) + np.pi, np.arccos(-v.y))
            uv = Vector2(longlat.x / (2 * np.pi), longlat.y / np.pi)
        except RuntimeWarning:
            uv = Vector2.zero()
        # uv.y = 1f - uv.y;
        # uv.x = 1f - uv.x;

        return {'result': True, 'hit_point': hit_point, 'normal' : normal, 'uv' : uv}

    @staticmethod
    def parse(data):
        # print('parsing data ' + str(data))
        sphere = Sphere(1.0)

        if 'radius' in data:
            sphere.radius = float(data['radius'])

        if 'transform' in data:
            sphere.transform.parse(data['transform'])

        if 'color' in data:
            color = data['color']
            sphere.albedo = Color(color[0], color[1], color[2], color[3])

        return sphere
