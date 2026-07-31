from miru.raymarching.sdfbase import SDFObject


def _validate_smoothing(smoothing, operation_name):
    if smoothing <= 0.0:
        raise ValueError(f"{operation_name} smoothing must be positive")
    return float(smoothing)


def smooth_min(left_distance, right_distance, smoothing):
    """Polynomial smooth minimum used by smooth Boolean operations."""
    smoothing = _validate_smoothing(smoothing, "Smooth-minimum")
    blend = max(
        0.0,
        min(
            1.0,
            0.5
            + 0.5
            * (right_distance - left_distance)
            / smoothing,
        ),
    )
    return (
        right_distance * (1.0 - blend)
        + left_distance * blend
        - smoothing * blend * (1.0 - blend)
    )


def smooth_max(left_distance, right_distance, smoothing):
    """Polynomial smooth maximum, derived from the smooth minimum."""
    return -smooth_min(-left_distance, -right_distance, smoothing)


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


class SDFIntersection(SDFBinaryOperation):
    def distance(self, position):
        return max(
            self.left.distance(position),
            self.right.distance(position),
        )


class SDFSmoothUnion(SDFBinaryOperation):
    def __init__(self, left, right, smoothing, color=None):
        super().__init__(left, right, color=color)
        self.smoothing = _validate_smoothing(smoothing, "Smooth-union")

    def distance(self, position):
        left_distance = self.left.distance(position)
        right_distance = self.right.distance(position)
        return smooth_min(
            left_distance,
            right_distance,
            self.smoothing,
        )


class SDFSmoothIntersection(SDFBinaryOperation):
    def __init__(self, left, right, smoothing, color=None):
        super().__init__(left, right, color=color)
        self.smoothing = _validate_smoothing(
            smoothing,
            "Smooth-intersection",
        )

    def distance(self, position):
        return smooth_max(
            self.left.distance(position),
            self.right.distance(position),
            self.smoothing,
        )


class SDFSmoothSubtraction(SDFBinaryOperation):
    """Smoothly subtract the right-hand SDF from the left-hand SDF."""

    def __init__(self, left, right, smoothing, color=None):
        super().__init__(left, right, color=color)
        self.smoothing = _validate_smoothing(
            smoothing,
            "Smooth-subtraction",
        )

    def distance(self, position):
        return smooth_max(
            self.left.distance(position),
            -self.right.distance(position),
            self.smoothing,
        )
