import copy
import json
from pathlib import Path
import tempfile
import unittest

from miru.engine.scene_manifest import SceneManifestError, validate_scene_manifest
from miru.raymarching.scene import (
    load_scene_manifest as load_raymarch_manifest,
    load_scene_manifest_data as load_raymarch_manifest_data,
)
from miru.raymarching.sdfcube import SDFCube
from miru.raymarching.sdfplane import SDFPlane
from miru.raymarching.sdfsphere import SDFSphere
from miru.raymarching.sdftorus import SDFTorus
from miru.raytracing.scene import load_scene_manifest_data as load_raytrace_manifest_data
from miru.raytracing.sphere import Sphere


def minimal_manifest(renderer="raymarching"):
    return {
        "version": 1,
        "renderer": renderer,
        "camera": {},
        "lights": [],
        "objects": [],
    }


class SceneManifestLoadingTests(unittest.TestCase):
    def test_documented_raymarch_example_loads_all_scene_data(self):
        repository_root = Path(__file__).resolve().parents[3]
        manifest_path = repository_root / "examples/scenes/raymarch_material_presets.json"

        scene = load_raymarch_manifest(manifest_path)

        self.assertEqual(len(scene.objects), 5)
        self.assertIsInstance(scene.objects[0], SDFSphere)
        self.assertIsInstance(scene.objects[1], SDFCube)
        self.assertIsInstance(scene.objects[2], SDFTorus)
        self.assertIsInstance(scene.objects[4], SDFPlane)
        self.assertEqual(
            [obj.material.preset for obj in scene.objects],
            ["matte", "metal", "glass-like", "emissive", "matte"],
        )
        self.assertEqual(len(scene.get_lights()), 2)
        self.assertEqual(scene.get_light(), scene.get_lights()[0])
        self.assertEqual(scene.camera.transform.position.z, -7.0)
        self.assertNotEqual(scene.camera.transform.forward.y, 0.0)
        self.assertEqual(scene.render_width, 480)
        self.assertEqual(scene.render_height, 270)
        self.assertEqual(scene.target_image_file, "raymarch_material_presets.png")
        self.assertAlmostEqual(scene.background_color.b, 0.06)

    def test_valid_raytrace_manifest_uses_renderer_specific_objects(self):
        data = minimal_manifest("raytracing")
        data["camera"] = {
            "near": 0.1,
            "far": 50,
            "transform": {"position": [1, 2, -3]},
        }
        data["lights"] = [
            {
                "type": "point",
                "intensity": 2,
                "color": [1, 0.8, 0.6, 1],
            }
        ]
        data["objects"] = [
            {
                "id": "subject",
                "type": "sphere",
                "radius": 2,
                "transform": {"position": [0, 0, 5]},
                "material": {"preset": "matte", "albedo": [0.2, 0.4, 0.6]},
            },
            {
                "type": "cube",
                "transform": {"position": [3, 0, 7]},
                "material": {"preset": "metal"},
            },
        ]
        data["render"] = {"width": 64, "height": 32, "ssaa": 2}

        scene = load_raytrace_manifest_data(data, source="raytrace-test")

        self.assertIsInstance(scene.objects[0], Sphere)
        self.assertEqual(scene.objects[0].radius, 2.0)
        self.assertEqual(scene.objects[0].material.preset, "matte")
        self.assertEqual(len(scene.get_lights()), 1)
        self.assertEqual(scene.ssaa_level, 2)

    def test_empty_light_and_object_arrays_are_valid(self):
        scene = load_raymarch_manifest_data(minimal_manifest())

        self.assertEqual(scene.objects, [])
        self.assertEqual(scene.get_lights(), [])
        self.assertIsNone(scene.get_light())

    def test_formal_schema_is_checked_in_and_declares_v1(self):
        schema_path = (
            Path(__file__).resolve().parents[1]
            / "miru/engine/scene_manifest.schema.json"
        )
        with schema_path.open("r", encoding="utf-8") as schema_file:
            schema = json.load(schema_file)

        self.assertEqual(schema["properties"]["version"]["const"], 1)
        self.assertFalse(schema["additionalProperties"])


class SceneManifestValidationTests(unittest.TestCase):
    def assert_manifest_error(self, data, path, message=None):
        with self.assertRaises(SceneManifestError) as raised:
            validate_scene_manifest(data, source="invalid-scene")
        self.assertIn(path, str(raised.exception))
        if message is not None:
            self.assertIn(message, str(raised.exception))

    def test_root_must_be_an_object(self):
        self.assert_manifest_error([], "$", "expected an object")

    def test_required_root_sections_are_enforced(self):
        for name in ("version", "renderer", "camera", "lights", "objects"):
            with self.subTest(name=name):
                data = minimal_manifest()
                del data[name]
                self.assert_manifest_error(data, "$." + name, "missing required")

    def test_version_renderer_and_renderer_mismatch_are_rejected(self):
        data = minimal_manifest()
        data["version"] = 2
        self.assert_manifest_error(data, "$.version", "version 1")

        data = minimal_manifest()
        data["renderer"] = "gpu"
        self.assert_manifest_error(data, "$.renderer", "expected one of")

        with self.assertRaisesRegex(SceneManifestError, "expected renderer 'raytracing'"):
            load_raytrace_manifest_data(minimal_manifest())

    def test_unknown_properties_are_rejected_at_every_level(self):
        data = minimal_manifest()
        data["surprise"] = True
        self.assert_manifest_error(data, "$.surprise", "unknown property")

        data = minimal_manifest()
        data["camera"]["look_at"] = [0, 0, 1]
        self.assert_manifest_error(data, "$.camera.look_at", "unknown property")

    def test_camera_clip_planes_and_vectors_are_validated(self):
        data = minimal_manifest()
        data["camera"] = {"near": 2, "far": 1}
        self.assert_manifest_error(data, "$.camera.far", "greater than")

        data = minimal_manifest()
        data["camera"] = {"fov": 180}
        self.assert_manifest_error(data, "$.camera.fov", "less than 180")

        data = minimal_manifest()
        data["camera"] = {"transform": {"position": [0, 1]}}
        self.assert_manifest_error(data, "$.camera.transform.position", "three numbers")

    def test_colors_and_render_dimensions_are_validated(self):
        data = minimal_manifest()
        data["background_color"] = [0, 1.1, 0]
        self.assert_manifest_error(data, "$.background_color[1]", "no greater")

        data = minimal_manifest()
        data["render"] = {"width": 0}
        self.assert_manifest_error(data, "$.render.width", "at least 1")

    def test_object_types_geometry_and_duplicate_ids_are_validated(self):
        data = minimal_manifest()
        data["objects"] = [{"type": "capsule"}]
        self.assert_manifest_error(data, "$.objects[0].type", "unsupported")

        data = minimal_manifest()
        data["objects"] = [{"type": "sphere"}]
        self.assert_manifest_error(data, "$.objects[0].radius", "missing required")

        data = minimal_manifest()
        data["objects"] = [{"type": "cube", "size": [1, -1, 1]}]
        self.assert_manifest_error(data, "$.objects[0].size[1]", "positive")

        data = minimal_manifest()
        data["objects"] = [
            {"id": "same", "type": "sphere", "radius": 1},
            {"id": "same", "type": "sphere", "radius": 2},
        ]
        self.assert_manifest_error(data, "$.objects[1].id", "duplicate")

    def test_material_preset_and_parameters_are_validated(self):
        data = minimal_manifest()
        data["objects"] = [
            {
                "type": "sphere",
                "radius": 1,
                "material": {"preset": "plastic"},
            }
        ]
        self.assert_manifest_error(data, "$.objects[0].material.preset", "unknown")

        data = copy.deepcopy(data)
        data["objects"][0]["material"] = {
            "preset": "glass-like",
            "roughness": -0.1,
        }
        self.assert_manifest_error(data, "$.objects[0].material.roughness", "at least")

    def test_boolean_values_are_not_accepted_as_numbers(self):
        data = minimal_manifest()
        data["render"] = {"width": True}
        self.assert_manifest_error(data, "$.render.width", "integer")


class SceneManifestFileErrorTests(unittest.TestCase):
    def test_malformed_json_reports_line_and_column(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as manifest:
            manifest.write('{\n  "version": 1,\n  bad\n}')
            path = Path(manifest.name)
        try:
            with self.assertRaisesRegex(SceneManifestError, r"line 3, column"):
                load_raymarch_manifest(path)
        finally:
            path.unlink()

    def test_non_finite_json_number_is_rejected(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as manifest:
            manifest.write(
                '{"version":1,"renderer":"raymarching","camera":{},'
                '"lights":[],"objects":[],"background_color":[NaN,0,0]}'
            )
            path = Path(manifest.name)
        try:
            with self.assertRaisesRegex(SceneManifestError, "non-finite number"):
                load_raymarch_manifest(path)
        finally:
            path.unlink()

    def test_yaml_has_a_clear_dependency_free_error(self):
        with self.assertRaisesRegex(SceneManifestError, "YAML is not supported"):
            load_raymarch_manifest("scene.yaml")

    def test_missing_file_is_wrapped_with_source_context(self):
        with self.assertRaises(SceneManifestError) as raised:
            load_raymarch_manifest("definitely-missing-scene.json")
        self.assertIn("definitely-missing-scene.json", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
