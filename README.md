# miru
Rendering experiments (Python, CPP)

## Rendering experiments using Python

Simple raytracing, to run you should type:
```bash
python simpleraytracing/test.py
```
![Rendered image](https://raw.githubusercontent.com/adrianogil/miru/main/examples/raytracing_pymiru.png)


## Rendering experiments using CPP

### Dependencies

On MacOS install:

```bash
brew install png++
```

![Rendered image](https://raw.githubusercontent.com/adrianogil/miru/main/examples/raymarching_cpp_sphere.png )


## Planned features

## Composable signed distance fields

The Python ray-marching package includes exact primitives, Boolean operations,
distance modifiers, and coordinate-domain transformations:

- sphere, box, plane, and torus primitives;
- union, intersection, subtraction, and smooth variants;
- shell/onion and rounding modifiers;
- elongation, infinite repetition, twisting, and bending;
- central-difference normals shared by primitive and composed fields.

Boolean and distance-modifier operations preserve a direct relationship with
the underlying signed distances. Non-rigid domain transformations such as
twisting and bending generally produce conservative distance estimators rather
than mathematically exact SDFs, so renderers should use a safety factor while
sphere tracing them.

Run the tests:

```bash
PYTHONPATH=src/python python3 -m unittest discover -s src/python/tests -v
```

Render ten examples and their comparison gallery:

```bash
PYTHONPATH=src/python python3 \
  src/python/examples/render_sdf_operations_gallery.py \
  examples/sdf_operations
```

![Expanded SDF operations](examples/sdf_operations/sdf_operations_gallery.png)

## Raymarch material presets

Every SDF object can use one of four named local-shading presets:

| Preset | Intended appearance | Main parameters |
| --- | --- | --- |
| `matte` | diffuse, rough surface | `albedo`, `roughness` |
| `metal` | tinted specular metal | `albedo`, `roughness`, `metallic` |
| `glass-like` | background-tinted Fresnel surface | `albedo`, `roughness`, `transmission`, `ior` |
| `emissive` | unlit self-illumination | `emission`, `emission_strength` |

Apply a preset directly in Python:

```python
from miru.raymarching import SDFSphere

sphere = SDFSphere(1.0).set_material_preset(
    "metal",
    albedo=[0.85, 0.62, 0.22],
    roughness=0.18,
)
```

`glass-like` is deliberately named as an approximation: the current
single-hit marcher provides Fresnel and transmission-colored local shading,
but does not trace secondary refraction rays.

## Versioned scene manifests

The strict scene loader reads camera, point lights, renderer-specific objects,
materials, background, and render settings from a versioned JSON document.
The formal contract is
[`scene_manifest.schema.json`](src/python/miru/engine/scene_manifest.schema.json).
Version 1 requires these top-level fields:

| Field | Value |
| --- | --- |
| `version` | integer `1` |
| `renderer` | `raymarching` or `raytracing` |
| `camera` | camera settings and optional transform |
| `lights` | array of point lights; may be empty |
| `objects` | array of objects supported by the selected renderer |

Transforms accept `position`, `rotation`, and `scale` three-number arrays.
Raymarch manifests support `sphere`, `cube`, `plane`, and `torus`; CPU
ray-tracing manifests support `sphere` and `cube`. Unknown properties and
object types are rejected with a source path and JSON-path-like location.

Load and render the documented preset scene:

```bash
PYTHONPATH=src/python python3 - <<'PY'
from miru.raymarching.scene import load_scene_manifest

scene = load_scene_manifest("examples/scenes/raymarch_material_presets.json")
scene.render()
PY
```

The loader is dependency-free and JSON-only. YAML files produce an explicit
unsupported-format error rather than relying on an optional undeclared parser.
The older unversioned `.scene` files remain available through `SceneParser`.


## Contributing

Feel free to submit PRs. I will do my best to review and merge them if I consider them essential.

## Development status

This is a very alpha software. The code was written with no consideration of coding standards and architecture. A refactoring would do it good...

## See also
