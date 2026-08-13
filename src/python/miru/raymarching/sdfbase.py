from miru.engine.color import Color
from miru.engine.material import Material
from miru.engine.transform import Transform
from miru.engine.vector import Vector3


class SDFUtils:
    @staticmethod
    def get_normal(distance_method, current_pos, epsilon=0.001):
        """Estimate an SDF surface normal with central differences."""
        eps_x = Vector3(epsilon, 0.0, 0.0)
        eps_y = Vector3(0.0, epsilon, 0.0)
        eps_z = Vector3(0.0, 0.0, epsilon)

        normal_x = (
            distance_method(current_pos.add(eps_x))
            - distance_method(current_pos.minus(eps_x))
        )
        normal_y = (
            distance_method(current_pos.add(eps_y))
            - distance_method(current_pos.minus(eps_y))
        )
        normal_z = (
            distance_method(current_pos.add(eps_z))
            - distance_method(current_pos.minus(eps_z))
        )

        return Vector3(normal_x, normal_y, normal_z).normalized()


class SDFObject:
    """Common scene-facing behavior for signed distance field objects."""

    def __init__(self, color=None):
        self.transform = Transform()
        self.material = Material.default()
        self.color = color if color is not None else Color.random()

    @property
    def color(self):
        return self.material.albedo

    @color.setter
    def color(self, value):
        self.material.albedo = value

    @property
    def albedo(self):
        return self.color

    @albedo.setter
    def albedo(self, value):
        self.color = value

    def pre_render(self):
        self.transform.update_internals()

    def render(self, scene, interception):
        interception["normal"] = SDFUtils.get_normal(
            self.distance,
            interception["hit_point"],
        )
        return self.material.render(scene, interception)

    def set_material_preset(self, preset, **overrides):
        """Apply a named raymarch material preset and return this object."""
        self.material = Material.from_preset(preset, **overrides)
        return self
