from vector import Vector3

import numpy as np

import transformutils as t_utils

class Transform:
    def __init__(self):
        self.position = Vector3(0,0,0)
        self.rotation = Vector3(0,0,0)
        self.scale = Vector3.one()

        self.forward = Vector3(0,0,1)
        self.right = Vector3(1,0,0)
        self.left = Vector3(-1,0,0)
        self.up = Vector3(0,1,0)

    def get_transform_matrix(self):
        return t_utils.getTranslationMatrix(self.position).dot(
                t_utils.getOrientationMatrix(self.rotation)
            ).dot(t_utils.getScalingMatrix(self.scale))

    def apply_transform(self, v):
        new_value = self.get_transform_matrix().dot(v.homo_value())
        return Vector3(new_value[0], new_value[1], new_value[2])