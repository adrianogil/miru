from transform import Transform

from vector import Vector3

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

    def intercepts(self, ray):
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

                a = self.boundary_points[0].minus(intersection_point).normalized()
                b = self.boundary_points[1].minus(intersection_point).normalized()

                N = a.cross_product(b).normalized()

                for i in range(1, len(self.boundary_points)):
                    p = self.boundary_points[i]
                    if intersection_point.equals(p):
                        return (True, intersection_point)
                    a = self.boundary_points[i].minus(intersection_point).normalized()
                    b = self.boundary_points[(i+1)%len(self.boundary_points)].minus(intersection_point).normalized()
                    Nt = a.cross_product(b).normalized()
                    if N.dot_product(Nt) < 0:
                        return (False, Vector3.zero())
                    # print('Passed on ' + str(i))

                return (True, intersection_point)

        return (False, Vector3.zero())