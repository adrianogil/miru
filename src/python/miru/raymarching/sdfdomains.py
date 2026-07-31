import math

from miru.engine.vector import Vector3
from miru.raymarching.sdfmodifiers import SDFUnaryOperation


def _componentwise_clamp(value, minimum, maximum):
    return Vector3(
        max(minimum.x, min(maximum.x, value.x)),
        max(minimum.y, min(maximum.y, value.y)),
        max(minimum.z, min(maximum.z, value.z)),
    )


def _wrapped_component(value, period):
    return (value + period * 0.5) % period - period * 0.5


def _rotate_xy(value, angle):
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return Vector3(
        cosine * value.x - sine * value.y,
        sine * value.x + cosine * value.y,
        value.z,
    )


def _rotate_xz(value, angle):
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return Vector3(
        cosine * value.x - sine * value.z,
        value.y,
        sine * value.x + cosine * value.z,
    )


class SDFDomainOperation(SDFUnaryOperation):
    """Base class for inverse mappings applied before SDF evaluation."""

    def __init__(self, child, center=None, color=None):
        super().__init__(child, color=color)
        self.center = center.clone() if center is not None else Vector3.zero()

    def map_position(self, position):
        return position

    def distance(self, position):
        return self.child.distance(self.map_position(position))


class SDFElongation(SDFDomainOperation):
    def __init__(self, child, half_length, center=None, color=None):
        if min(half_length.x, half_length.y, half_length.z) < 0.0:
            raise ValueError("Elongation half lengths must not be negative")

        super().__init__(child, center=center, color=color)
        self.half_length = half_length.clone()

    def map_position(self, position):
        local = position.minus(self.center)
        extent = self.half_length
        clamped = _componentwise_clamp(
            local,
            extent.multiply(-1.0),
            extent,
        )
        return local.minus(clamped).add(self.center)


class SDFRepeat(SDFDomainOperation):
    VALID_AXES = frozenset(("x", "y", "z"))

    def __init__(self, child, period, axes=("x", "y", "z"), center=None, color=None):
        axes = frozenset(axes)
        if not axes:
            raise ValueError("Repetition requires at least one axis")
        if not axes.issubset(self.VALID_AXES):
            raise ValueError("Repetition axes must be x, y, or z")
        for axis in axes:
            if getattr(period, axis) <= 0.0:
                raise ValueError("Repetition periods must be positive")

        super().__init__(child, center=center, color=color)
        self.period = period.clone()
        self.axes = axes

    def map_position(self, position):
        local = position.minus(self.center)
        values = {"x": local.x, "y": local.y, "z": local.z}
        for axis in self.axes:
            values[axis] = _wrapped_component(
                values[axis],
                getattr(self.period, axis),
            )
        return Vector3(values["x"], values["y"], values["z"]).add(self.center)


class SDFTwist(SDFDomainOperation):
    """Twist a field around the Y axis by ``strength`` radians per unit."""

    def __init__(self, child, strength, center=None, color=None):
        super().__init__(child, center=center, color=color)
        self.strength = float(strength)

    def map_position(self, position):
        local = position.minus(self.center)
        return _rotate_xz(local, -self.strength * local.y).add(self.center)


class SDFBend(SDFDomainOperation):
    """Bend a field in the XY plane as X moves away from the pivot."""

    def __init__(self, child, strength, center=None, color=None):
        super().__init__(child, center=center, color=color)
        self.strength = float(strength)

    def map_position(self, position):
        local = position.minus(self.center)
        return _rotate_xy(local, -self.strength * local.x).add(self.center)
