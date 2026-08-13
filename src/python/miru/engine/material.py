from .color import Color

from miru.engine.shaders import (
    EmissiveShader,
    GlassLikeShader,
    LambertianTintShader,
    MatteShader,
    MetalShader,
    UnlitShader,
)


MATERIAL_PRESETS = ("matte", "metal", "glass-like", "emissive")


class Material:
    def __init__(self):
        self.texture = None
        self.albedo = Color(1.0, 1.0, 1.0, 1.0)
        self.shader = UnlitShader()
        self.preset = None
        self.roughness = 0.5
        self.metallic = 0.0
        self.transmission = 0.0
        self.ior = 1.0
        self.emission = None
        self.emission_strength = 0.0
        self.debug_mode = False
        self.debug_render_type = "None"

    def clone(self):
        new_material = Material()
        new_material.albedo = self.albedo.clone()
        new_material.texture = self.texture
        new_material.shader = self.shader
        new_material.preset = self.preset
        new_material.roughness = self.roughness
        new_material.metallic = self.metallic
        new_material.transmission = self.transmission
        new_material.ior = self.ior
        new_material.emission = (
            None if self.emission is None else self.emission.clone()
        )
        new_material.emission_strength = self.emission_strength
        new_material.debug_mode = self.debug_mode
        new_material.debug_render_type = self.debug_render_type

        return new_material

    def set_texture(self, texture):
        self.texture = texture

    def set_shader(self, shader):
        self.shader = shader

    def render(self, scene, interception):
        if self.debug_mode:
            return self.debug_render(scene, interception)

        return self.shader.frag_render(self, scene, interception)

    def debug_render(self, scene, interception):
        c = Color.white()
        if self.debug_render_type == "normal":
            c.set_rgb(interception['normal'])
        return c

    @staticmethod
    def default():
        material = Material()
        material.shader = UnlitShader()

        return material

    @staticmethod
    def preset_names():
        return MATERIAL_PRESETS

    @classmethod
    def from_preset(cls, name, **overrides):
        if name not in MATERIAL_PRESETS:
            raise ValueError(
                "Unknown material preset %r; expected one of %s"
                % (name, ", ".join(MATERIAL_PRESETS))
            )

        material = cls()
        material.preset = name
        if name == "matte":
            material.shader = MatteShader()
            material.roughness = 0.9
        elif name == "metal":
            material.shader = MetalShader()
            material.roughness = 0.15
            material.metallic = 1.0
        elif name == "glass-like":
            material.shader = GlassLikeShader()
            material.roughness = 0.05
            material.transmission = 0.92
            material.ior = 1.5
        elif name == "emissive":
            material.shader = EmissiveShader()
            material.emission_strength = 1.0

        for key, value in overrides.items():
            if not hasattr(material, key):
                raise ValueError("Unknown material property %r" % key)
            if key in ("albedo", "emission") and value is not None:
                value = value if isinstance(value, Color) else Color.from_array(value)
            setattr(material, key, value)

        material._validate_properties()
        return material

    @classmethod
    def matte(cls, **overrides):
        return cls.from_preset("matte", **overrides)

    @classmethod
    def metal(cls, **overrides):
        return cls.from_preset("metal", **overrides)

    @classmethod
    def glass_like(cls, **overrides):
        return cls.from_preset("glass-like", **overrides)

    @classmethod
    def emissive(cls, **overrides):
        return cls.from_preset("emissive", **overrides)

    def _validate_properties(self):
        for name in ("roughness", "metallic", "transmission"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError("Material %s must be between 0 and 1" % name)
        if self.ior < 1.0:
            raise ValueError("Material ior must be at least 1")
        if self.emission_strength < 0.0:
            raise ValueError("Material emission_strength must not be negative")

    @staticmethod
    def parse(data):
        if not isinstance(data, dict):
            raise ValueError("Material data must be an object")

        if 'preset' in data:
            material = Material.from_preset(data['preset'])
        else:
            material = Material()

        if 'shader' in data:
            shader_name = data['shader']

            if shader_name == 'unlit':
                material.shader = UnlitShader()
            elif shader_name == "lambertian":
                material.shader = LambertianTintShader()

        if 'albedo' in data:
            material.albedo = Color.from_array(data['albedo'])

        for property_name in ("roughness", "metallic", "transmission", "ior"):
            if property_name in data:
                setattr(material, property_name, float(data[property_name]))

        if 'emission' in data:
            material.emission = Color.from_array(data['emission'])

        if 'emission_strength' in data:
            material.emission_strength = float(data['emission_strength'])

        if 'debug' in data:
            if 'active' in data['debug']:
                active = data['debug']['active']
                debug_mode = active if isinstance(active, bool) else active == "True"
                material.debug_mode = debug_mode
            else:
                material.debug_mode = True
            if 'render' in data['debug']:
                material.debug_render_type = data['debug']['render']

        material._validate_properties()
        return material
