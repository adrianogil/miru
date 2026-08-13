import unittest

from miru.engine.color import Color
from miru.engine.light import Light
from miru.engine.material import Material
from miru.engine.shaders import (
    EmissiveShader,
    GlassLikeShader,
    MatteShader,
    MetalShader,
)
from miru.engine.vector import Vector3
from miru.raymarching import MATERIAL_PRESETS, SDFSphere, material_from_preset


class FakeScene:
    def __init__(self, lights=None):
        self.lights = list(lights or [])
        self.background_color = Color.black()

    def get_lights(self):
        return self.lights


def hit(normal=None, view_direction=None):
    return {
        "hit_point": Vector3.zero(),
        "normal": normal or Vector3.forward().multiply(-1.0),
        "view_direction": view_direction or Vector3.forward(),
    }


class MaterialPresetTests(unittest.TestCase):
    def test_all_named_presets_have_expected_shader_and_defaults(self):
        expected = {
            "matte": (MatteShader, 0.0, 0.0),
            "metal": (MetalShader, 1.0, 0.0),
            "glass-like": (GlassLikeShader, 0.0, 0.92),
            "emissive": (EmissiveShader, 0.0, 0.0),
        }

        self.assertEqual(MATERIAL_PRESETS, tuple(expected))
        for name, (shader_type, metallic, transmission) in expected.items():
            material = material_from_preset(name)
            self.assertEqual(material.preset, name)
            self.assertIsInstance(material.shader, shader_type)
            self.assertEqual(material.metallic, metallic)
            self.assertEqual(material.transmission, transmission)

    def test_presets_are_fresh_and_accept_overrides(self):
        first = Material.metal(albedo=[0.2, 0.3, 0.4], roughness=0.4)
        second = Material.metal()

        first.albedo.r = 0.9
        self.assertEqual(first.roughness, 0.4)
        self.assertEqual(second.roughness, 0.15)
        self.assertEqual(second.albedo.r, 1.0)

    def test_invalid_preset_and_properties_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown material preset"):
            Material.from_preset("plastic")
        with self.assertRaisesRegex(ValueError, "roughness"):
            Material.matte(roughness=1.1)
        with self.assertRaisesRegex(ValueError, "ior"):
            Material.glass_like(ior=0.9)
        with self.assertRaisesRegex(ValueError, "emission_strength"):
            Material.emissive(emission_strength=-1.0)

    def test_parse_applies_preset_then_explicit_overrides(self):
        material = Material.parse(
            {
                "preset": "glass-like",
                "albedo": [0.1, 0.2, 0.3],
                "roughness": 0.2,
                "ior": 1.33,
            }
        )

        self.assertEqual(material.preset, "glass-like")
        self.assertEqual(material.albedo.a, 1.0)
        self.assertEqual(material.roughness, 0.2)
        self.assertEqual(material.ior, 1.33)

    def test_clone_copies_all_preset_state_without_sharing_colors(self):
        original = Material.emissive(
            albedo=[0.2, 0.3, 0.4],
            emission=[0.8, 0.5, 0.1],
            emission_strength=2.0,
        )
        original.debug_mode = True
        clone = original.clone()

        clone.albedo.r = 1.0
        clone.emission.g = 1.0
        self.assertEqual(original.albedo.r, 0.2)
        self.assertEqual(original.emission.g, 0.5)
        self.assertEqual(clone.preset, "emissive")
        self.assertEqual(clone.emission_strength, 2.0)
        self.assertTrue(clone.debug_mode)


class MaterialPresetShaderTests(unittest.TestCase):
    def setUp(self):
        light = Light()
        light.transform.position = Vector3(0.0, 0.0, -2.0)
        self.lit_scene = FakeScene([light])

    def test_matte_responds_to_surface_orientation(self):
        material = Material.matte(albedo=[0.5, 0.4, 0.3])
        lit = material.render(self.lit_scene, hit())
        dark = material.render(
            self.lit_scene,
            hit(normal=Vector3.forward()),
        )

        self.assertGreater(lit.r, dark.r)

    def test_metal_produces_view_dependent_highlight(self):
        material = Material.metal(albedo=[0.8, 0.6, 0.2], roughness=0.1)
        head_on = material.render(self.lit_scene, hit())
        off_axis = material.render(
            self.lit_scene,
            hit(view_direction=Vector3(1.0, 0.0, 1.0).normalized()),
        )

        self.assertGreater(head_on.r, off_axis.r)

    def test_glass_like_has_stronger_fresnel_at_grazing_angles(self):
        material = Material.glass_like(albedo=[0.8, 0.9, 1.0])
        scene = FakeScene()
        head_on = material.render(scene, hit())
        grazing = material.render(
            scene,
            hit(view_direction=Vector3(1.0, 0.0, 0.01).normalized()),
        )

        self.assertGreater(grazing.r, head_on.r)

    def test_emissive_requires_no_light(self):
        material = Material.emissive(
            emission=[0.25, 0.5, 0.75],
            emission_strength=2.0,
        )

        rendered = material.render(FakeScene(), hit())
        self.assertEqual(rendered.to_tuple(3), (127, 255, 255))

    def test_sdf_object_convenience_api_uses_preset(self):
        sphere = SDFSphere(1.0).set_material_preset(
            "emissive",
            albedo=[0.3, 0.2, 0.1],
        )
        rendered = sphere.render(
            FakeScene(),
            {"hit_point": Vector3(1.0, 0.0, 0.0)},
        )

        self.assertEqual(sphere.material.preset, "emissive")
        self.assertEqual(rendered.to_tuple(3), (76, 51, 25))


if __name__ == "__main__":
    unittest.main()
