from transform import Transform

from vector import Vector3

import numpy as np

class Sphere:
    def __init__(self, radius):
        self.radius = radius

        self.albedo = (255,0,0)

        self.transform = Transform()

    def intercepts(self, ray):
        # geometric solution
        # https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-sphere-intersection

        # print('Sphere intercepts ray ' + str(ray))

        radius2 = self.radius * self.radius

        L = self.transform.position.minus(ray.origin)
        tca = L.dot_product(ray.direction)

        d2 = L.dot_product(L) - tca * tca
        if d2 > radius2:
            return (False, Vector3.zero);
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
                return (False, Vector3.zero); # both t0 and t1 are negative
        t = t0;

        return (True, ray.origin.add(ray.direction.multiply(t)));