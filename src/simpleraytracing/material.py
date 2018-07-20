from color import Color

class Material:
    def __init__(self):
        self.texture = None
        self.albedo = Color(1.0, 1.0, 1.0, 1.0)
        self.shader = None

    def clone(self):
        new_material = Material()
        new_material.albedo = self.albedo
        new_material.texture = self.texture
        new_material.shader = self.shader

        return new_material

    def set_texture(self, texture):
        self.texture = texture

    def set_shader(self, shader):
        self.shader = shader

    def render(self, scene, interception):
        return self.shader.frag_render(self, scene, interception)