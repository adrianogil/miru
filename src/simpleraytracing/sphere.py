from transform import Transform

from vector import Vector3
from color import Color

import numpy as np

class Sphere:
    def __init__(self, radius):
        self.radius = radius

        self.albedo = Color(1.0, 0.0, 0.0, 1.0)

        self.transform = Transform()

        self.material = None

    def pre_render(self):
        pass

    def set_material(self, material):
        self.material = material

    def render(self, scene, interception):
        if self.material != None:
            return self.material.render(scene, interception)

        light = scene.get_light()

        if light is None:
            return self.albedo
        else:
            render_color = self.albedo.clone()

            light_direction = light.transform.position.minus(interception['hit_point']).normalized()
            dotNL = light_direction.dot_product(interception['normal'])
            # print("Dot light and normal: " + str(dotNL))
            rgb_value = render_color.rgb().multiply(max(0.0, dotNL))
            rgb_value = rgb_value.multiply(light.intensity)
            render_color.set_rgb(rgb_value)

            return render_color

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
            return {'result': False, 'hit_point': Vector3.zero, 'normal' : None}
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
                return {'result': False, 'hit_point': Vector3.zero, 'normal' : None} # both t0 and t1 are negative
        t = t0;

        hit_point = ray.origin.add(ray.direction.multiply(t))
        normal = hit_point.minus(self.transform.position).normalized()

        return {'result': True, 'hit_point': hit_point, 'normal' : normal}