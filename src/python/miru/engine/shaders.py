class UnlitShader:
    def __init__(self):
        pass

    def frag_render(self, material, scene, interception):
        render_color = material.albedo.clone()

        # print("unlitshader::frag_render")

        if 'uv' in interception:
            uv = interception['uv']
            if material.texture is not None:
                render_color = render_color.tint(material.texture.tex2D(uv))

        return render_color


class LambertianTintShader:
    def __init__(self):
        pass

    def frag_render(self, material, scene, interception):
        light = scene.get_light()

        render_color = material.albedo.clone()

        if 'uv' in interception:
            uv = interception['uv']
            if material.texture is not None:
                render_color = render_color.tint(material.texture.tex2D(uv))

        light_direction = light.transform.position.minus(interception['hit_point']).normalized()
        dotNL = max(interception['normal'].dot_product(light_direction), 0.0)
        # print("Dot light and normal: " + str(dotNL))
        rgb_value = render_color.rgb().multiply(dotNL)
        rgb_value = rgb_value.multiply(light.intensity)
        rgb_value = rgb_value.scale(light.color.rgb())
        render_color.set_rgb(rgb_value)

        return render_color
