from color import Color

from miru.engine.shaders import UnlitShader, LambertianTintShader


class Material:
    def __init__(self):
        self.texture = None
        self.albedo = Color(1.0, 1.0, 1.0, 1.0)
        self.shader = UnlitShader()
        self.debug_mode = False
        self.debug_render_type = "None"

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

        if 'debug' in data:
            if 'active' in data['debug']:
                debug_mode = data['debug']['active'] == "True"
                material.debug_mode = debug_mode
            else:
                material.debug_mode = True
            if 'render' in data['debug']:
                material.debug_render_type = data['debug']['render']

        return material
