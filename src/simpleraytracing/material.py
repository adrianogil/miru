from color import Color

class Material:
    def __init__(self):
        self.texture = None
        self.albedo = Color()

    def set_texture(texture):
        self.texture = texture

    def render(self, scene, interception):
        render_color = self.albedo.clone()

        uv = interception['uv']

        if self.texture != None:
            render_color = render_color * self.texture.tex2D(uv)

        light_direction = light.transform.position.minus(interception['hit_point']).normalized()
        dotNL = light_direction.dot_product(interception['normal'])
        # print("Dot light and normal: " + str(dotNL))
        rgb_value = render_color.rgb().multiply(max(0.0, dotNL))
        rgb_value = rgb_value.multiply(light.intensity)
        render_color.set_rgb(rgb_value)

        return render_color