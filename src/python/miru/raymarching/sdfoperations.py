from miru.raymarching.sdfbase import SDFObject


class SDFBinaryOperation(SDFObject):
    def __init__(self, left, right, color=None):
        if left is None or right is None:
            raise ValueError("SDF operations require two operands")

        super().__init__(color=color)
        self.left = left
        self.right = right

    def pre_render(self):
        super().pre_render()
        self.left.pre_render()
        self.right.pre_render()


class SDFUnion(SDFBinaryOperation):
    def distance(self, position):
        return min(
            self.left.distance(position),
            self.right.distance(position),
        )


class SDFSubtraction(SDFBinaryOperation):
    """Subtract the right-hand SDF from the left-hand SDF."""

    def distance(self, position):
        return max(
            self.left.distance(position),
            -self.right.distance(position),
        )


class SDFSmoothUnion(SDFBinaryOperation):
    def __init__(self, left, right, smoothing, color=None):
        if smoothing <= 0.0:
            raise ValueError("Smooth-union smoothing must be positive")

        super().__init__(left, right, color=color)
        self.smoothing = float(smoothing)

    def distance(self, position):
        left_distance = self.left.distance(position)
        right_distance = self.right.distance(position)
        blend = max(
            0.0,
            min(
                1.0,
                0.5
                + 0.5
                * (right_distance - left_distance)
                / self.smoothing,
            ),
        )

        return (
            right_distance * (1.0 - blend)
            + left_distance * blend
            - self.smoothing * blend * (1.0 - blend)
        )
