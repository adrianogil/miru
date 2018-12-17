from miru.engine.transform import Transform
from miru.engine.vector import Vector3, Vector2

from miru.engine.material import Material

import numpy as np

try:
    range = xrange
except NameError:
    pass

class Plane:
    def __init__(self, points):
        self.n = points[1].minus(points[0]).normalized().cross_product(points[2].minus(points[0]).normalized()).normalized()
        self.p0 = points[0]
        self.boundary_points = points
        self.albedo = (0,255,0)
        self.transform = Transform()
        self.material = Material.default()

    def pre_render(self):
        self.transform.update_internals()

        points = []

        for p in self.boundary_points:
            points.append(self.transform.apply_transform(p))

        self.n = points[1].minus(points[0]).normalized().cross_product(points[2].minus(points[0]).normalized()).normalized()
        self.p0 = points[0]

        self.points = points

    def render(self, scene, interception):
        if self.material != None:
            return self.material.render(scene, interception)

        print('no material')

        return self.albedo

    def intercepts(self, ray):
        
        points = self.points

        # https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-plane-and-ray-disk-intersection
        denom = self.n.dot_product(ray.direction)
        # print(str(denom))
        if np.abs(denom) > 1e-6:
            if denom < 0:
                self.n.multiply(-1, False)
            p0l0 = self.p0.minus(ray.origin)
            t = p0l0.dot_product(self.n)

            if t >= 0:
                intersection_point = ray.origin.add(ray.direction.multiply(t))

                a = points[0].minus(intersection_point).normalized()
                b = points[1].minus(intersection_point).normalized()

                N = a.cross_product(b).normalized()

                for i in range(1, len(points)):
                    p = points[i]
                    if intersection_point.equals(p):
                        return (True, intersection_point)
                    a = points[i].minus(intersection_point).normalized()
                    b = points[(i+1)%len(points)].minus(intersection_point).normalized()
                    Nt = a.cross_product(b).normalized()
                    if N.dot_product(Nt) < 0:
                        return {'result': False, 'hit_point': Vector3.zero, 'normal' : None, 'uv' : Vector2.zero}
                    # print('Passed on ' + str(i))

                return {'result': True, 'hit_point': intersection_point, 'normal' : None, 'uv' : Vector2.zero}

        return {'result': False, 'hit_point': Vector3.zero, 'normal' : None, 'uv' : Vector2.zero} 