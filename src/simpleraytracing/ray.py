class Ray:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

        self.origin = p1
        self.direction = p2.minus(p1).normalized()