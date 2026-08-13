"""Strict, dependency-free loading for versioned Miru JSON scenes."""

import json
from pathlib import Path

from miru.engine.camera import Camera
from miru.engine.color import Color
from miru.engine.light import Light
from miru.engine.material import MATERIAL_PRESETS, Material


SUPPORTED_RENDERERS = ("raymarching", "raytracing")


class SceneManifestError(ValueError):
    """A scene manifest error with source and JSON-path context."""

    def __init__(self, message, path="$", source="<memory>"):
        self.message = message
        self.path = path
        self.source = str(source)
        super().__init__(self.__str__())

    def __str__(self):
        return "%s: %s: %s" % (self.source, self.path, self.message)


def _fail(message, path, source):
    raise SceneManifestError(message, path=path, source=source)


def _expect_mapping(value, path, source):
    if not isinstance(value, dict):
        _fail("expected an object", path, source)


def _expect_keys(value, allowed, required, path, source):
    _expect_mapping(value, path, source)
    unknown = sorted(set(value) - set(allowed))
    if unknown:
        _fail("unknown property %r" % unknown[0], "%s.%s" % (path, unknown[0]), source)
    missing = sorted(set(required) - set(value))
    if missing:
        _fail("missing required property", "%s.%s" % (path, missing[0]), source)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _number(value, path, source, minimum=None, maximum=None, exclusive=False):
    if not _is_number(value):
        _fail("expected a number", path, source)
    if minimum is not None:
        valid = value > minimum if exclusive else value >= minimum
        if not valid:
            qualifier = "greater than" if exclusive else "at least"
            _fail("expected a number %s %s" % (qualifier, minimum), path, source)
    if maximum is not None and value > maximum:
        _fail("expected a number no greater than %s" % maximum, path, source)


def _integer(value, path, source, minimum=1):
    if not isinstance(value, int) or isinstance(value, bool):
        _fail("expected an integer", path, source)
    if value < minimum:
        _fail("expected an integer at least %s" % minimum, path, source)


def _vector(value, path, source, positive=False, nonzero=False):
    if not isinstance(value, list) or len(value) != 3:
        _fail("expected an array of three numbers", path, source)
    for index, component in enumerate(value):
        _number(component, "%s[%s]" % (path, index), source)
        if positive and component <= 0.0:
            _fail("expected a positive number", "%s[%s]" % (path, index), source)
    if nonzero and all(component == 0.0 for component in value):
        _fail("expected a non-zero vector", path, source)


def _color(value, path, source):
    if not isinstance(value, list) or len(value) not in (3, 4):
        _fail("expected an RGB or RGBA array", path, source)
    for index, component in enumerate(value):
        _number(component, "%s[%s]" % (path, index), source, 0.0, 1.0)


def _validate_transform(data, path, source):
    _expect_keys(
        data,
        allowed=("position", "rotation", "scale"),
        required=(),
        path=path,
        source=source,
    )
    if "position" in data:
        _vector(data["position"], path + ".position", source)
    if "rotation" in data:
        _vector(data["rotation"], path + ".rotation", source)
    if "scale" in data:
        _vector(data["scale"], path + ".scale", source, nonzero=True)


def _validate_camera(data, path, source):
    _expect_keys(
        data,
        allowed=("mode", "fov", "near", "far", "transform"),
        required=(),
        path=path,
        source=source,
    )
    if "mode" in data and data["mode"] not in ("perspective", "orthographic"):
        _fail("expected 'perspective' or 'orthographic'", path + ".mode", source)
    if "fov" in data:
        _number(data["fov"], path + ".fov", source, 0.0, 180.0, exclusive=True)
        if data["fov"] >= 180.0:
            _fail("expected a number less than 180", path + ".fov", source)
    near = data.get("near", 0.01)
    far = data.get("far", 1000.0)
    _number(near, path + ".near", source, 0.0, exclusive=True)
    _number(far, path + ".far", source, 0.0, exclusive=True)
    if far <= near:
        _fail("must be greater than camera near", path + ".far", source)
    if "transform" in data:
        _validate_transform(data["transform"], path + ".transform", source)


def _validate_light(data, path, source):
    _expect_keys(
        data,
        allowed=("type", "color", "intensity", "transform"),
        required=("type",),
        path=path,
        source=source,
    )
    if data["type"] != "point":
        _fail("only point lights are supported", path + ".type", source)
    if "color" in data:
        _color(data["color"], path + ".color", source)
    if "intensity" in data:
        _number(data["intensity"], path + ".intensity", source, 0.0)
    if "transform" in data:
        _validate_transform(data["transform"], path + ".transform", source)


def _validate_material(data, path, source):
    _expect_keys(
        data,
        allowed=(
            "preset",
            "albedo",
            "roughness",
            "metallic",
            "transmission",
            "ior",
            "emission",
            "emission_strength",
        ),
        required=("preset",),
        path=path,
        source=source,
    )
    if data["preset"] not in MATERIAL_PRESETS:
        _fail(
            "unknown preset %r; expected one of %s"
            % (data["preset"], ", ".join(MATERIAL_PRESETS)),
            path + ".preset",
            source,
        )
    if "albedo" in data:
        _color(data["albedo"], path + ".albedo", source)
    if "emission" in data:
        _color(data["emission"], path + ".emission", source)
    for name in ("roughness", "metallic", "transmission"):
        if name in data:
            _number(data[name], path + "." + name, source, 0.0, 1.0)
    if "ior" in data:
        _number(data["ior"], path + ".ior", source, 1.0)
    if "emission_strength" in data:
        _number(data["emission_strength"], path + ".emission_strength", source, 0.0)


_COMMON_OBJECT_KEYS = ("id", "type", "transform", "material")
_GEOMETRY_KEYS = {
    "raymarching": {
        "sphere": ("radius",),
        "cube": ("size",),
        "plane": ("normal", "offset"),
        "torus": ("major_radius", "minor_radius"),
    },
    "raytracing": {
        "sphere": ("radius",),
        "cube": (),
    },
}
_REQUIRED_GEOMETRY_KEYS = {
    "raymarching": {
        "sphere": ("radius",),
        "cube": ("size",),
        "plane": ("normal",),
        "torus": ("major_radius", "minor_radius"),
    },
    "raytracing": {
        "sphere": ("radius",),
        "cube": (),
    },
}


def _validate_object(data, renderer, path, source):
    _expect_mapping(data, path, source)
    if "type" not in data:
        _fail("missing required property", path + ".type", source)
    object_type = data["type"]
    geometry = _GEOMETRY_KEYS[renderer]
    if object_type not in geometry:
        _fail(
            "unsupported %s object type %r" % (renderer, object_type),
            path + ".type",
            source,
        )
    _expect_keys(
        data,
        allowed=_COMMON_OBJECT_KEYS + geometry[object_type],
        required=("type",) + _REQUIRED_GEOMETRY_KEYS[renderer][object_type],
        path=path,
        source=source,
    )
    if "id" in data and (not isinstance(data["id"], str) or not data["id"]):
        _fail("expected a non-empty string", path + ".id", source)
    if "transform" in data:
        _validate_transform(data["transform"], path + ".transform", source)
    if "material" in data:
        _validate_material(data["material"], path + ".material", source)

    if object_type == "sphere" and "radius" in data:
        _number(data["radius"], path + ".radius", source, 0.0, exclusive=True)
    elif object_type == "cube" and renderer == "raymarching" and "size" in data:
        _vector(data["size"], path + ".size", source, positive=True)
    elif object_type == "plane":
        if "normal" in data:
            _vector(data["normal"], path + ".normal", source, nonzero=True)
        if "offset" in data:
            _number(data["offset"], path + ".offset", source)
    elif object_type == "torus":
        for name in ("major_radius", "minor_radius"):
            if name in data:
                _number(data[name], path + "." + name, source, 0.0, exclusive=True)


def _validate_render(data, path, source):
    _expect_keys(
        data,
        allowed=("width", "height", "ssaa", "to_image"),
        required=(),
        path=path,
        source=source,
    )
    for name in ("width", "height", "ssaa"):
        if name in data:
            _integer(data[name], path + "." + name, source)
    if "to_image" in data and (
        not isinstance(data["to_image"], str) or not data["to_image"]
    ):
        _fail("expected a non-empty string", path + ".to_image", source)


def validate_scene_manifest(data, source="<memory>", expected_renderer=None):
    """Validate a decoded scene manifest and return it unchanged."""
    _expect_keys(
        data,
        allowed=(
            "version",
            "renderer",
            "camera",
            "lights",
            "objects",
            "render",
            "background_color",
        ),
        required=("version", "renderer", "camera", "lights", "objects"),
        path="$",
        source=source,
    )
    if data["version"] != 1 or isinstance(data["version"], bool):
        _fail("only scene manifest version 1 is supported", "$.version", source)
    renderer = data["renderer"]
    if renderer not in SUPPORTED_RENDERERS:
        _fail(
            "expected one of %s" % ", ".join(SUPPORTED_RENDERERS),
            "$.renderer",
            source,
        )
    if expected_renderer is not None and renderer != expected_renderer:
        _fail(
            "expected renderer %r" % expected_renderer,
            "$.renderer",
            source,
        )

    _validate_camera(data["camera"], "$.camera", source)
    if not isinstance(data["lights"], list):
        _fail("expected an array", "$.lights", source)
    for index, light in enumerate(data["lights"]):
        _validate_light(light, "$.lights[%s]" % index, source)
    if not isinstance(data["objects"], list):
        _fail("expected an array", "$.objects", source)

    ids = set()
    for index, obj in enumerate(data["objects"]):
        object_path = "$.objects[%s]" % index
        _validate_object(obj, renderer, object_path, source)
        if "id" in obj:
            if obj["id"] in ids:
                _fail("duplicate object id %r" % obj["id"], object_path + ".id", source)
            ids.add(obj["id"])

    if "render" in data:
        _validate_render(data["render"], "$.render", source)
    if "background_color" in data:
        _color(data["background_color"], "$.background_color", source)
    return data


def read_scene_manifest(path, expected_renderer=None):
    """Read and validate a JSON manifest without constructing a scene."""
    source_path = Path(path)
    if source_path.suffix.lower() in (".yaml", ".yml"):
        raise SceneManifestError(
            "YAML is not supported; use a JSON scene manifest",
            source=str(source_path),
        )
    try:
        with source_path.open("r", encoding="utf-8") as manifest_file:
            data = json.load(
                manifest_file,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError("non-finite number %s" % value)
                ),
            )
    except json.JSONDecodeError as error:
        raise SceneManifestError(
            "invalid JSON at line %s, column %s: %s"
            % (error.lineno, error.colno, error.msg),
            source=str(source_path),
        ) from error
    except (OSError, ValueError) as error:
        raise SceneManifestError(str(error), source=str(source_path)) from error
    return validate_scene_manifest(
        data,
        source=str(source_path),
        expected_renderer=expected_renderer,
    )


class SceneManifestLoader:
    """Construct one renderer's scene from the shared manifest contract."""

    def __init__(self, renderer, scene_factory, object_parsers):
        if renderer not in SUPPORTED_RENDERERS:
            raise ValueError("Unsupported renderer %r" % renderer)
        self.renderer = renderer
        self.scene_factory = scene_factory
        self.object_parsers = dict(object_parsers)

    def load(self, path):
        data = read_scene_manifest(path, expected_renderer=self.renderer)
        return self.load_data(data, source=str(path), validate=False)

    def load_data(self, data, source="<memory>", validate=True):
        if validate:
            validate_scene_manifest(
                data,
                source=source,
                expected_renderer=self.renderer,
            )

        scene = self.scene_factory()
        camera = Camera.parse(data["camera"])
        camera.transform.update_internals()
        scene.set_camera(camera)

        for light_data in data["lights"]:
            light = Light.parse(light_data)
            light.transform.update_internals()
            scene.add_light(light)

        for index, object_data in enumerate(data["objects"]):
            parser = self.object_parsers[object_data["type"]]
            try:
                obj = parser(object_data)
                if "material" in object_data:
                    obj.material = Material.parse(object_data["material"])
            except (KeyError, TypeError, ValueError) as error:
                raise SceneManifestError(
                    str(error),
                    path="$.objects[%s]" % index,
                    source=source,
                ) from error
            scene.add_objects(obj)

        if "background_color" in data:
            scene.background_color = Color.from_array(data["background_color"])
        render = data.get("render", {})
        scene.render_width = render.get("width", scene.render_width)
        scene.render_height = render.get("height", scene.render_height)
        scene.set_ssaa(render.get("ssaa", scene.ssaa_level))
        scene.target_image_file = render.get("to_image", scene.target_image_file)
        return scene
