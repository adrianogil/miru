#!/usr/bin/env python3
"""Render a visual gallery of Miru's SDF primitives and operations."""

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from miru.engine.color import Color
from miru.engine.vector import Vector3
from miru.raymarching import (
    SDFCube,
    SDFPlane,
    SDFSmoothUnion,
    SDFSphere,
    SDFSubtraction,
    SDFTorus,
    SDFUnion,
)
from miru.raymarching.sdfbase import SDFUtils


EPSILON = 0.006
MAX_DISTANCE = 30.0
MAX_STEPS = 96


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def multiply(vector, scalar):
    return tuple(component * scalar for component in vector)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def normalize(vector):
    magnitude = math.sqrt(dot(vector, vector))
    return tuple(component / magnitude for component in vector)


def as_vector3(vector):
    return Vector3(vector[0], vector[1], vector[2])


def set_position(sdf, x, y, z):
    sdf.transform.position = Vector3(x, y, z)
    return sdf


def set_color(sdf, color):
    sdf.color = Color(color[0], color[1], color[2], 1.0)
    return sdf


def create_gallery_objects():
    box = set_color(
        set_position(SDFCube(Vector3(1.65, 1.65, 1.65)), 0.0, -0.28, 0.0),
        (0.31, 0.78, 1.0),
    )
    sphere = set_color(
        set_position(SDFSphere(0.96), 0.0, -0.25, 0.0),
        (1.0, 0.47, 0.34),
    )
    torus = set_color(
        set_position(SDFTorus(0.76, 0.27), 0.0, -0.18, 0.0),
        (0.67, 0.45, 1.0),
    )

    union_sphere = set_position(SDFSphere(0.78), -0.42, -0.30, 0.0)
    union_box = set_position(
        SDFCube(Vector3(1.15, 1.15, 1.15)),
        0.42,
        -0.32,
        0.0,
    )
    union = set_color(
        SDFUnion(union_sphere, union_box),
        (0.32, 0.91, 0.63),
    )

    subtraction_outer = set_position(
        SDFCube(Vector3(1.85, 1.85, 1.85)),
        0.0,
        -0.20,
        0.0,
    )
    subtraction_cutter = set_position(
        SDFSphere(0.92),
        0.56,
        0.12,
        -0.48,
    )
    subtraction = set_color(
        SDFSubtraction(subtraction_outer, subtraction_cutter),
        (1.0, 0.70, 0.25),
    )

    smooth_sphere = set_position(SDFSphere(0.78), -0.48, -0.30, 0.0)
    smooth_torus = set_position(SDFTorus(0.68, 0.25), 0.45, -0.22, 0.0)
    smooth_union = set_color(
        SDFSmoothUnion(
            smooth_sphere,
            smooth_torus,
            smoothing=0.48,
        ),
        (1.0, 0.37, 0.71),
    )

    return [
        ("Exact box", "signed exterior + interior", box),
        ("Sphere", "translated radial distance", sphere),
        ("Plane + torus", "infinite ground + Y-axis ring", torus),
        ("Union", "min(left, right)", union),
        ("Subtraction", "max(left, -right)", subtraction),
        ("Smooth union", "polynomial distance blend", smooth_union),
    ]


def raymarch(ray_origin, ray_direction, objects):
    distance_traveled = 0.0

    for step in range(MAX_STEPS):
        position = add(ray_origin, multiply(ray_direction, distance_traveled))
        point = as_vector3(position)
        distances = [sdf.distance(point) for sdf in objects]
        nearest_index = min(
            range(len(distances)),
            key=distances.__getitem__,
        )
        nearest_distance = distances[nearest_index]

        if nearest_distance < EPSILON:
            return position, nearest_index, step

        distance_traveled += max(nearest_distance, EPSILON * 0.5)
        if distance_traveled > MAX_DISTANCE:
            break

    return None


def background_color(y, height, ray_direction):
    horizon = max(0.0, min(1.0, 0.5 + ray_direction[1] * 0.7))
    vertical = y / max(height - 1, 1)
    glow = (1.0 - vertical) * 0.035
    return (
        0.035 + 0.055 * horizon + glow,
        0.045 + 0.070 * horizon + glow,
        0.085 + 0.105 * horizon + glow,
    )


def shade(hit, ray_direction, sdf, is_ground, step):
    point = as_vector3(hit)
    normal_vector = SDFUtils.get_normal(sdf.distance, point, epsilon=0.002)
    normal = (normal_vector.x, normal_vector.y, normal_vector.z)
    light_direction = normalize((-0.55, 0.85, -0.38))
    view_direction = multiply(ray_direction, -1.0)

    diffuse = max(0.0, dot(normal, light_direction))
    half_vector = normalize(add(light_direction, view_direction))
    specular = max(0.0, dot(normal, half_vector)) ** 42
    rim = (1.0 - max(0.0, dot(normal, view_direction))) ** 2
    step_attenuation = 1.0 - min(step / MAX_STEPS, 1.0) * 0.18

    if is_ground:
        checker = (
            math.floor(hit[0] * 1.4)
            + math.floor(hit[2] * 1.4)
        ) % 2
        base = (0.12, 0.14, 0.19) if checker else (0.19, 0.21, 0.27)
        diffuse_light = 0.46 + 0.42 * diffuse
        color = tuple(component * diffuse_light for component in base)
    else:
        base = (sdf.color.r, sdf.color.g, sdf.color.b)
        diffuse_light = 0.22 + 0.78 * diffuse
        color = tuple(
            component * diffuse_light * step_attenuation
            + 0.20 * rim * component
            + 0.32 * specular
            for component in base
        )

    fog = min(max((math.sqrt(dot(hit, hit)) - 3.5) / 10.0, 0.0), 0.42)
    fog_color = (0.075, 0.085, 0.13)
    color = tuple(
        component * (1.0 - fog) + fog_component * fog
        for component, fog_component in zip(color, fog_color)
    )

    return tuple(
        int(255 * max(0.0, min(1.0, component)) ** (1.0 / 2.2))
        for component in color
    )


def render_panel(sdf, width, height):
    image = Image.new("RGB", (width, height))
    pixels = image.load()

    ground = set_color(
        SDFPlane(Vector3.up(), offset=-1.18),
        (0.17, 0.19, 0.24),
    )
    objects = [sdf, ground]

    camera_origin = (4.25, 3.0, -5.4)
    camera_target = (0.0, -0.22, 0.0)
    camera_forward = normalize(subtract(camera_target, camera_origin))
    camera_right = normalize(cross(camera_forward, (0.0, 1.0, 0.0)))
    camera_up = normalize(cross(camera_right, camera_forward))
    field_of_view = math.radians(42.0)
    view_scale = math.tan(field_of_view * 0.5)
    aspect_ratio = width / height

    for y in range(height):
        screen_y = (1.0 - 2.0 * (y + 0.5) / height) * view_scale
        for x in range(width):
            screen_x = (
                (2.0 * (x + 0.5) / width - 1.0)
                * aspect_ratio
                * view_scale
            )
            ray_direction = normalize(
                add(
                    camera_forward,
                    add(
                        multiply(camera_right, screen_x),
                        multiply(camera_up, screen_y),
                    ),
                )
            )
            result = raymarch(camera_origin, ray_direction, objects)

            if result is None:
                base = background_color(y, height, ray_direction)
                pixels[x, y] = tuple(int(component * 255) for component in base)
                continue

            hit, object_index, step = result
            pixels[x, y] = shade(
                hit,
                ray_direction,
                objects[object_index],
                object_index == 1,
                step,
            )

    return image


def load_font(size, bold=False):
    candidates = [
        (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Arial.ttf"
        ),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ),
    ]

    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)

    return ImageFont.load_default()


def compose_gallery(panel_width, panel_height, scale):
    gallery_objects = create_gallery_objects()
    gap = 16 * scale
    margin = 26 * scale
    header_height = 92 * scale
    caption_height = 52 * scale
    rendered_width = panel_width * scale
    rendered_height = panel_height * scale
    card_width = rendered_width
    card_height = rendered_height + caption_height
    canvas_width = margin * 2 + card_width * 3 + gap * 2
    canvas_height = margin * 2 + header_height + card_height * 2 + gap

    canvas = Image.new("RGB", (canvas_width, canvas_height), (12, 15, 27))
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(28 * scale, bold=True)
    subtitle_font = load_font(11 * scale)
    label_font = load_font(15 * scale, bold=True)
    detail_font = load_font(10 * scale)

    draw.text(
        (margin, margin),
        "Miru SDF Foundation",
        font=title_font,
        fill=(239, 244, 255),
    )
    draw.text(
        (margin, margin + 40 * scale),
        "Exact distance primitives • composable operations • CPU sphere tracing",
        font=subtitle_font,
        fill=(139, 158, 196),
    )

    for index, (label, detail, sdf) in enumerate(gallery_objects):
        column = index % 3
        row = index // 3
        left = margin + column * (card_width + gap)
        top = margin + header_height + row * (card_height + gap)

        draw.rounded_rectangle(
            (
                left - 2 * scale,
                top - 2 * scale,
                left + card_width + 2 * scale,
                top + card_height + 2 * scale,
            ),
            radius=10 * scale,
            fill=(25, 30, 48),
            outline=(57, 68, 103),
            width=1 * scale,
        )

        panel = render_panel(sdf, panel_width, panel_height)
        panel = panel.resize(
            (rendered_width, rendered_height),
            resample=Image.Resampling.LANCZOS,
        )
        canvas.paste(panel, (left, top))

        accent = (
            int(sdf.color.r * 255),
            int(sdf.color.g * 255),
            int(sdf.color.b * 255),
        )
        caption_top = top + rendered_height
        draw.rounded_rectangle(
            (
                left + 12 * scale,
                caption_top + 12 * scale,
                left + 18 * scale,
                caption_top + 38 * scale,
            ),
            radius=3 * scale,
            fill=accent,
        )
        draw.text(
            (left + 28 * scale, caption_top + 8 * scale),
            label,
            font=label_font,
            fill=(236, 241, 255),
        )
        draw.text(
            (left + 28 * scale, caption_top + 29 * scale),
            detail,
            font=detail_font,
            fill=(131, 148, 184),
        )

    return canvas


def main():
    parser = argparse.ArgumentParser(
        description="Render a gallery of Miru's SDF foundation.",
    )
    parser.add_argument("output", type=Path, help="Target PNG file")
    parser.add_argument("--panel-width", type=int, default=200)
    parser.add_argument("--panel-height", type=int, default=140)
    parser.add_argument("--scale", type=int, default=2)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    gallery = compose_gallery(
        panel_width=args.panel_width,
        panel_height=args.panel_height,
        scale=args.scale,
    )
    gallery.save(args.output)
    print(
        f"Rendered {gallery.width}x{gallery.height} SDF gallery to "
        f"{args.output}"
    )


if __name__ == "__main__":
    main()
