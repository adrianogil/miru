import numpy as np

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def value(self):
        return [[self.x],[self.y],[self.z]]

    def homo_value(self):
        return [[self.x],[self.y],[self.z],[1]]

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    def clone(self):
        return Vector3(self.x, self.y, self.z)

    def equals(self, v):
        return self.x == v.x and self.y == v.y and self.z == v.z

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

    # def scalar_cross_product(self, v1, v2, cloneit=True)
    #     return (self.x - v1.x)*(v2.y - v1.y)*(v2.z - v1.z) - (self.y - v1.y)*(v2.x - v1.x)*(v2.z - v1.z) - \
    #         (self.z - v1.z)*(v2.x - v1.x)*(v2.z - v1.z)

    def cross_product(self, v, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.cross_product(v,False)
            return new_v
        else:
            new_x = self.y*v.z - self.z*v.y
            new_y = self.z*v.x - self.x*v.z
            new_z = self.x*v.y - self.y*v.x

            self.x = new_x
            self.y = new_y
            self.z = new_z
            return self

    @staticmethod
    def zero():
        return Vector3(0.0,0.0,0.0)

    @staticmethod
    def one():
        return Vector3(1.0,1.0,1.0)

    @staticmethod
    def up():
        return Vector3(0.0,1.0,0.0)



def createVector(x,y,z):
    return Vector3(x,y,z)


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def value(self):
        return [[self.x],[self.y]]

    def homo_value(self):
        return [[self.x],[self.y],[1]]

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def clone(self):
        return Vector2(self.x, self.y)

    def equals(self, v):
        return self.x == v.x and self.y == v.y

    def multiply(self, p, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.multiply(p, False)
            return new_v
        else:
            self.x = self.x * p
            self.y = self.y * p
            return self

    def add(self, v, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.add(v, False)
            return new_v
        else:
            self.x = self.x + v.x
            self.y = self.y + v.y
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
        return np.sqrt(self.x*self.x + self.y*self.y)

    def normalized(self, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.normalized(False)
            return new_v
        else:
            self.multiply(1.0/self.magnitude(), False)
            return self

    def dot_product(self, v):
        dot_value = self.x*v.x + self.y*v.y
        return dot_value

    @staticmethod
    def zero():
        return Vector2(0.0,0.0)

    @staticmethod
    def one():
        return Vector2(1.0,1.0)

    @staticmethod
    def up():
        return Vector2(0.0,1.0)

def createVector2(x,y):
    return Vector2(x,y)