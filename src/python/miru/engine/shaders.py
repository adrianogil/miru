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


def _base_color(material, interception):
    render_color = material.albedo.clone()
    if 'uv' in interception and material.texture is not None:
        render_color = render_color.tint(material.texture.tex2D(interception['uv']))
    return render_color


def _scene_lights(scene):
    if hasattr(scene, "get_lights"):
        lights = scene.get_lights()
        if lights:
            return lights
    light = scene.get_light()
    return [] if light is None else [light]


def _clamp_color(color):
    color.r = min(max(color.r, 0.0), 1.0)
    color.g = min(max(color.g, 0.0), 1.0)
    color.b = min(max(color.b, 0.0), 1.0)
    color.a = min(max(color.a, 0.0), 1.0)
    return color


class LambertianTintShader:
    def __init__(self):
        pass

    def frag_render(self, material, scene, interception):
        render_color = _base_color(material, interception)
        lights = _scene_lights(scene)
        if not lights:
            return render_color

        accumulated = render_color.rgb().multiply(0.0)
        for light in lights:
            light_direction = light.transform.position.minus(
                interception['hit_point']
            ).normalized()
            dot_nl = max(interception['normal'].dot_product(light_direction), 0.0)
            contribution = render_color.rgb().multiply(dot_nl * light.intensity)
            accumulated = accumulated.add(contribution.scale(light.color.rgb()))

        render_color.set_rgb(accumulated)
        return _clamp_color(render_color)


class MatteShader(LambertianTintShader):
    """Diffuse local illumination used by the matte material preset."""


class MetalShader:
    """A compact local-light approximation for polished metal surfaces."""

    def frag_render(self, material, scene, interception):
        base = _base_color(material, interception)
        lights = _scene_lights(scene)
        if not lights:
            return base

        normal = interception['normal']
        view_direction = interception.get('view_direction')
        if view_direction is None:
            view = normal
        else:
            view = view_direction.multiply(-1.0).normalized()

        accumulated = base.rgb().multiply(0.0)
        specular_power = 2.0 + (1.0 - material.roughness) * 126.0
        for light in lights:
            light_direction = light.transform.position.minus(
                interception['hit_point']
            ).normalized()
            half_vector = light_direction.add(view).normalized()
            diffuse = max(normal.dot_product(light_direction), 0.0)
            specular = max(normal.dot_product(half_vector), 0.0) ** specular_power
            intensity = light.intensity

            diffuse_rgb = base.rgb().multiply(
                diffuse * intensity * (1.0 - material.metallic)
            )
            specular_rgb = base.rgb().multiply(specular * intensity)
            contribution = diffuse_rgb.add(specular_rgb).scale(light.color.rgb())
            accumulated = accumulated.add(contribution)

        base.set_rgb(accumulated)
        return _clamp_color(base)


class GlassLikeShader:
    """Fresnel-tinted local shading for a transparent-looking surface.

    This intentionally remains a single-hit raymarch shader. It suggests glass
    by blending the scene background through the albedo and adding a Fresnel
    reflection term; it does not trace secondary refraction rays.
    """

    def frag_render(self, material, scene, interception):
        base = _base_color(material, interception)
        background = scene.background_color
        normal = interception['normal']
        view_direction = interception.get('view_direction')
        if view_direction is None:
            view = normal
        else:
            view = view_direction.multiply(-1.0).normalized()

        cos_theta = max(min(normal.dot_product(view), 1.0), 0.0)
        f0 = ((material.ior - 1.0) / (material.ior + 1.0)) ** 2
        fresnel = f0 + (1.0 - f0) * ((1.0 - cos_theta) ** 5)
        transmitted = background.tint(base).multiply(material.transmission)
        surface = base.multiply((1.0 - material.transmission) + fresnel)
        result = transmitted
        result.r += surface.r
        result.g += surface.g
        result.b += surface.b

        for light in _scene_lights(scene):
            light_direction = light.transform.position.minus(
                interception['hit_point']
            ).normalized()
            half_vector = light_direction.add(view).normalized()
            highlight = max(normal.dot_product(half_vector), 0.0) ** 96.0
            result.r += light.color.r * light.intensity * highlight
            result.g += light.color.g * light.intensity * highlight
            result.b += light.color.b * light.intensity * highlight

        return _clamp_color(result)


class EmissiveShader:
    """Unlit emission used by the emissive material preset."""

    def frag_render(self, material, scene, interception):
        emission = material.emission or _base_color(material, interception)
        return _clamp_color(emission.multiply(material.emission_strength))
