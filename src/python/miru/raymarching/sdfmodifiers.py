from miru.raymarching.sdfbase import SDFObject


class SDFUnaryOperation(SDFObject):
    """Base class for SDF operations with one child field."""

    def __init__(self, child, color=None):
        if child is None:
            raise ValueError("Unary SDF operations require a child")

        super().__init__(color=color)
        self.child = child

    def pre_render(self):
        super().pre_render()
        self.child.pre_render()


class SDFShell(SDFUnaryOperation):
    """Create a shell whose total thickness is twice ``thickness``."""

    def __init__(self, child, thickness, color=None):
        if thickness <= 0.0:
            raise ValueError("Shell thickness must be positive")

        super().__init__(child, color=color)
        self.thickness = float(thickness)

    def distance(self, position):
        return abs(self.child.distance(position)) - self.thickness


class SDFRound(SDFUnaryOperation):
    """Round and expand an SDF by its Minkowski radius."""

    def __init__(self, child, radius, color=None):
        if radius < 0.0:
            raise ValueError("Rounding radius must not be negative")

        super().__init__(child, color=color)
        self.radius = float(radius)

    def distance(self, position):
        return self.child.distance(position) - self.radius
