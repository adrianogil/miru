from color import Color

from engine.shaders import UnlitShader, LambertianTintShader

class Material:
    def __init__(self):
        self.texture = None
        self.albedo = Color(1.0, 1.0, 1.0, 1.0)
        self.shader = UnlitShader()

    def clone(self):
        new_material = Material()
        new_material.albedo = self.albedo.clone()
        new_material.texture = self.texture
        new_material.shader = self.shader

        return new_material

    def set_texture(self, texture):
        self.texture = texture

    def set_shader(self, shader):
        self.shader = shader

    def render(self, scene, interception):
        return self.shader.frag_render(self, scene, interception)

    @staticmethod
    def default():
        material = Material()
        material.shader = UnlitShader()

        return material

    @staticmethod
    def parse(data):
        material = Material()

        if 'shader' in data:
            shader_name = data['shader']

            if shader_name == 'unlit':
                material.shader = UnlitShader()
            elif shader_name == "lambertian":
                material.shader = LambertianTintShader()

        if 'albedo' in data:
            material.albedo = Color.from_array(data['albedo'])

        return material
