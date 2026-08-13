"""Material preset API for signed-distance-field raymarch objects."""

from miru.engine.material import MATERIAL_PRESETS, Material


def material_from_preset(name, **overrides):
    """Create a fresh material configured for the named raymarch preset."""
    return Material.from_preset(name, **overrides)


__all__ = ["MATERIAL_PRESETS", "Material", "material_from_preset"]
