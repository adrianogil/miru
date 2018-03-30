from transform import Transform

from plane import Plane

from vector import Vector3

import numpy as np

class Cube:
    def __init__(self, v1, v2, v3):
        
        ref_pos1 = v1.multiply(-0.5).add(v2.multiply(-0.5)).add(v3.multiply(-0.5))
        ref_pos2 = v1.multiply(0.5).add(v2.multiply(0.5)).add(v3.multiply(0.5))
        
        v1p = v1.multiply(-1)
        v2p = v2.multiply(-1)
        v3p = v3.multiply(-1)

        self.albedo = (255,0,0)

        self.transform = Transform()
        self.planes = [
            Plane([ref_pos1, ref_pos1.add(v1), ref_pos1.add(v1.add(v2)), ref_pos1.add(v2)]),
            Plane([ref_pos1, ref_pos1.add(v1), ref_pos1.add(v1.add(v3)), ref_pos1.add(v3)]),
            Plane([ref_pos1, ref_pos1.add(v2), ref_pos1.add(v2.add(v3)), ref_pos1.add(v2)]),
            Plane([ref_pos2, ref_pos2.add(v1p), ref_pos2.add(v1p.add(v2p)), ref_pos2.add(v2p)]),
            Plane([ref_pos2, ref_pos2.add(v1p), ref_pos2.add(v1p.add(v3p)), ref_pos2.add(v3p)]),
            Plane([ref_pos2, ref_pos2.add(v3p), ref_pos2.add(v3p.add(v2p)), ref_pos2.add(v2p)]),
        ]

    def intercepts(self, ray):
        for p in self.planes:
            p.transform.position = self.transform.position

        for p in self.planes:
            intersection_result = p.intercepts(ray)
            if intersection_result[0]:
                return intersection_result
        return (False, 0)
