from vector import Vector3

import random

class Color:
    def __init__(self, r, g, b, a):
        self.r = float(r)
        self.g = float(g)
        self.b = float(b)
        self.a = float(a)

    def __str__(self):
        return "(" + str(self.r) + ", " + str(self.g) + ", " + str(self.b) + ", " + str(self.a) + ")"

    def rgb(self):
        return Vector3(self.r, self.g, self.b)

    def set_rgb(self, rgb):
        self.r = rgb.x
        self.g = rgb.y
        self.b = rgb.z

    def to_tuple(self, size=4):
        if size == 1:
            return (int(255*self.r),)
        elif size == 2:
            return (int(255*self.r), int(255*self.g))
        elif size == 3:
            return (int(255*self.r), int(255*self.g), int(255*self.b))

        return (int(255*self.r), int(255*self.g), int(255*self.b), int(255*self.a))

    def clone(self):
        return Color(self.r, self.g, self.b, self.a)

    def multiply(self, p, cloneit=True):
        if cloneit:
            new_c = self.clone()
            new_c.multiply(p, False)
            return new_c
        else:

            self.r = self.r * p
            self.g = self.g * p
            self.b = self.b * p
            self.a = self.a * p

            return self

    def tint(self, color, cloneit=True):
        if cloneit:
            new_c = self.clone()
            new_c.tint(color, False)
            return new_c
        else:
            self.r = self.r * color.r
            self.g = self.g * color.g
            self.b = self.b * color.b
            self.a = self.a * color.a

            return self

    @staticmethod
    def random():
        return Color(float(random.randint(0,255))*1.0/255.0, float(random.randint(0,255))*1.0/255.0, float(random.randint(0,255))*1.0/255.0, 1.0)