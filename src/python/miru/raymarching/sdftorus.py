import math

from miru.raymarching.sdfbase import SDFObject


class SDFTorus(SDFObject):
    """Torus centered on the transform position and oriented around the Y axis."""

    def __init__(self, major_radius, minor_radius, color=None):
        if major_radius <= 0.0:
            raise ValueError("Torus major radius must be positive")
        if minor_radius <= 0.0:
            raise ValueError("Torus minor radius must be positive")

        super().__init__(color=color)
        self.major_radius = float(major_radius)
        self.minor_radius = float(minor_radius)

    def distance(self, position):
        local_position = position.minus(self.transform.position)
        radial_distance = math.sqrt(
            local_position.x * local_position.x
            + local_position.z * local_position.z
        )
        tube_x = radial_distance - self.major_radius

        return (
            math.sqrt(
                tube_x * tube_x
                + local_position.y * local_position.y
            )
            - self.minor_radius
        )
