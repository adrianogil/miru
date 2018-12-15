import random

from engine.transform import Transform
from engine.vector import Vector3, Vector2
from engine.color import Color

from raytracing.plane import Plane


class Cube:
    def __init__(self, v1=None, v2=None, v3=None):
        if v1 is None:
            v1 = Vector3.up()
        if v2 is None:
            v2 = Vector3.right()
        if v3 is None:
            v3 = Vector3.forward()

        ref_pos1 = v1.multiply(-0.5).add(v2.multiply(-0.5)).add(v3.multiply(-0.5))
        ref_pos2 = v1.multiply(0.5).add(v2.multiply(0.5)).add(v3.multiply(0.5))
        
        v1p = v1.multiply(-1)
        v2p = v2.multiply(-1)
        v3p = v3.multiply(-1)

        self.albedo = None

        self.transform = Transform()

        self.material = None

        self.transform = Transform()
        self.planes = [
            Plane([ref_pos1, ref_pos1.add(v1), ref_pos1.add(v1.add(v2)), ref_pos1.add(v2)]),
            Plane([ref_pos1, ref_pos1.add(v1), ref_pos1.add(v1.add(v3)), ref_pos1.add(v3)]),
            Plane([ref_pos1, ref_pos1.add(v2), ref_pos1.add(v2.add(v3)), ref_pos1.add(v2)]),
            Plane([ref_pos2, ref_pos2.add(v1p), ref_pos2.add(v1p.add(v2p)), ref_pos2.add(v2p)]),
            Plane([ref_pos2, ref_pos2.add(v1p), ref_pos2.add(v1p.add(v3p)), ref_pos2.add(v3p)]),
            Plane([ref_pos2, ref_pos2.add(v3p), ref_pos2.add(v3p.add(v2p)), ref_pos2.add(v2p)]),
        ]

        for p in self.planes:
            p.albedo = (random.randint(20,255), random.randint(20,255), random.randint(20,255))    

    def pre_render(self):
        self.transform.update_internals()
        for p in self.planes:
            p.transform = self.transform
            p.material = self.material
            p.pre_render()

    def render(self, scene, interception):
        if 'plane' in interception:
            return interception['plane'].render(scene, interception)

        print('no plane in interception')

        return self.albedo

    def intercepts(self, ray):
        min_depth_distance = 1000

        intersection = {'result': False, 'hit_point': Vector3.zero, 'normal' : None, 'uv' : Vector2.zero} 

        for p in self.planes:
            intersection_result = p.intercepts(ray)
            if intersection_result['result']:
                depth_distance = ray.origin.minus(intersection_result['hit_point']).magnitude()
                if depth_distance < min_depth_distance:
                    min_depth_distance = depth_distance
                    self.albedo = p.albedo
                    intersection['result'] = True
                    intersection['hit_point'] = intersection_result['hit_point']
                    intersection['plane'] = p

        return intersection

    @staticmethod
    def parse(data):
        # print('parsing data ' + str(data))
        cube = Cube()

        if 'transform' in data:
            cube.transform.parse(data['transform'])

        if 'color' in data:
            color = data['color']
            cube.color = Color(color[0], color[1], color[2], color[3])

        return cube
