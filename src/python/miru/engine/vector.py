import numpy as np


class Vector3:
    def __init__(self, x=None, y=None, z=None, array_data=None):
        self.values = np.zeros((3,))

        if array_data is not None:
            self.values = array_data.copy()
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if z is not None:
            self.z = z

    @property
    def x(self):
        return float(self.values[0])

    @x.setter
    def x(self, new_x):
        self.values[0] = new_x

    @property
    def y(self):
        return float(self.values[1])

    @y.setter
    def y(self, new_y):
        self.values[1] = new_y

    @property
    def z(self):
        return float(self.values[2])

    @z.setter
    def z(self, new_z):
        self.values[2] = new_z

    def value(self):
        return self.values.reshape(3, 1)

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
            self.values *= p
            return self

    def scale(self, v, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.scale(v, False)
            return new_v
        else:
            if v.__class__ == Vector3:
                self.values *= v.values
            else:
                self.values *= v
            return self

    def add(self, v, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.add(v, False)
            return new_v
        else:
            if v.__class__ == Vector3:
                self.values += v.values
            else:
                self.values += v
            return self

    def minus(self, v, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.minus(v, False)
            return new_v
        else:
            if v.__class__ == Vector3:
                self.values -= v.values
            else:
                self.values -= v
            return self

    def magnitude(self):
        return np.linalg.norm(self.values)

    def normalized(self, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.normalized(False)
            return new_v
        else:
            normalization_factor = np.linalg.norm(self.values)
            if normalization_factor == 0:
                normalization_factor = np.finfo(self.values.dtype).eps
            self.values = self.values / normalization_factor
            return self

    def dot_product(self, v):
        dot_value = self.values.transpose().dot(v.values).flatten()[0]
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
        return Vector3(0.0, 0.0, 0.0)

    @staticmethod
    def one():
        return Vector3(1.0, 1.0, 1.0)

    @staticmethod
    def up():
        return Vector3(0.0, 1.0, 0.0)

    @staticmethod
    def right():
        return Vector3(1.0, 0.0, 0.0)

    @staticmethod
    def forward():
        return Vector3(0.0, 0.0, 1.0)

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

    def scale(self, p, cloneit=True):
        if cloneit:
            new_v = self.clone()
            new_v.scale(p, False)
            return new_v
        else:
            self.x = self.x * p.x
            self.y = self.y * p.y
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
