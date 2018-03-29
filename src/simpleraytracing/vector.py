import numpy as np

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def value(self):
        return [[self.x],[self.y],[self.z]]

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    def clone(self):
        return Vector3(self.x, self.y, self.z)

    def multiply(self, p, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.multiply(p, False)
            return new_v
        else:
            self.x = self.x * p
            self.y = self.y * p
            self.z = self.z * p
            return self

    def add(self, v, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.add(v, False)
            return new_v
        else:
            self.x = self.x + v.x
            self.y = self.y + v.y
            self.z = self.z + v.z
            return self

    def minus(self, v, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.minus(v, False)
            return new_v
        else:
            self.add(v.clone().multiply(-1), False)
            return self

    def magnitude(self):
        return np.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    def normalized(self, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.normalized(False)
            return new_v
        else:
            self.multiply(1.0/self.magnitude(), False)
            return self

    def dot_product(self, v):
        dot_value = self.x*v.x + self.y*v.y + self.z*v.z
        return dot_value


def createVector(x,y,z):
    return Vector3(x,y,z)