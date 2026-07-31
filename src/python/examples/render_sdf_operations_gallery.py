#!/usr/bin/env python3
"""Render ten examples of Miru's extended SDF modeling operations."""

import argparse
import math
import multiprocessing
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from miru.engine.color import Color
from miru.engine.vector import Vector3
from miru.raymarching import (
    SDFBend,
    SDFCube,
    SDFElongation,
    SDFIntersection,
    SDFPlane,
    SDFRepeat,
    SDFRound,
    SDFShell,
    SDFSmoothIntersection,
    SDFSmoothSubtraction,
    SDFSmoothUnion,
    SDFSphere,
    SDFSubtraction,
    SDFTorus,
    SDFTwist,
)
from miru.raymarching.sdfbase import SDFUtils


EPSILON = 0.005
MAX_DISTANCE = 35.0
MAX_STEPS = 150
STEP_SAFETY = 0.72


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


def create_examples():
    intersection = SDFIntersection(
        SDFSphere(1.18),
        SDFCube(Vector3(1.75, 1.75, 1.75)),
    )

    smooth_intersection = SDFSmoothIntersection(
        SDFSphere(1.2),
        set_position(SDFCube(Vector3(1.75, 1.75, 1.75)), 0.3, 0.0, 0.0),
        smoothing=0.38,
    )

    smooth_subtraction = SDFSmoothSubtraction(
        SDFRound(SDFCube(Vector3(2.0, 1.8, 1.7)), radius=0.12),
        set_position(SDFSphere(0.95), 0.48, 0.25, -0.42),
        smoothing=0.28,
    )

    shell = SDFSubtraction(
        SDFShell(SDFSphere(1.08), thickness=0.105),
        set_position(SDFCube(Vector3(1.55, 2.4, 2.4)), 0.82, 0.0, 0.0),
    )

    rounded = SDFRound(
        SDFCube(Vector3(1.75, 1.45, 1.75)),
        radius=0.24,
    )

    elongated = SDFElongation(
        SDFSphere(0.52),
        half_length=Vector3(1.05, 0.0, 0.0),
    )

    repeated_sphere = set_position(SDFSphere(0.32), 0.0, -0.55, 0.0)
    repeated = SDFRepeat(
        repeated_sphere,
        period=Vector3(1.25, 1.0, 1.25),
        axes=("x", "z"),
    )

    twist_base = SDFRound(
        SDFCube(Vector3(1.15, 2.65, 1.15)),
        radius=0.11,
    )
    twisted = SDFTwist(twist_base, strength=1.12)

    bend_base = SDFRound(
        SDFCube(Vector3(3.2, 0.62, 0.78)),
        radius=0.14,
    )
    bent = SDFBend(bend_base, strength=0.52)

    link = SDFSmoothUnion(
        SDFElongation(
            SDFTorus(0.58, 0.17),
            half_length=Vector3(0.0, 0.36, 0.0),
        ),
        SDFTwist(
            SDFRound(SDFCube(Vector3(0.72, 2.05, 0.72)), radius=0.09),
            strength=1.25,
        ),
        smoothing=0.24,
    )
    composition = SDFSmoothSubtraction(
        link,
        set_position(SDFSphere(0.52), 0.18, 0.18, -0.15),
        smoothing=0.16,
    )

    specifications = [
        (
            "01_intersection",
            "Hard intersection",
            "max(d1, d2)",
            intersection,
            (0.22, 0.74, 1.0),
            (4.2, 2.8, -5.4),
            (0.0, 0.0, 0.0),
        ),
        (
            "02_smooth_intersection",
            "Smooth intersection",
            "smooth max rounds the seam",
            smooth_intersection,
            (0.35, 0.91, 0.65),
            (4.2, 2.8, -5.4),
            (0.05, 0.0, 0.0),
        ),
        (
            "03_smooth_subtraction",
            "Smooth subtraction",
            "rounded Boolean cavity",
            smooth_subtraction,
            (1.0, 0.62, 0.24),
            (4.3, 3.0, -5.5),
            (0.0, 0.0, 0.0),
        ),
        (
            "04_shell",
            "Shell / onion",
            "abs(d) - thickness",
            shell,
            (0.82, 0.45, 1.0),
            (4.1, 2.7, -5.2),
            (0.0, 0.0, 0.0),
        ),
        (
            "05_rounding",
            "Rounding",
            "Minkowski expansion by a sphere",
            rounded,
            (1.0, 0.38, 0.66),
            (4.2, 2.8, -5.4),
            (0.0, 0.0, 0.0),
        ),
        (
            "06_elongation",
            "Elongation",
            "sphere mapped into a capsule",
            elongated,
            (0.26, 0.88, 0.88),
            (4.5, 2.7, -5.5),
            (0.0, 0.0, 0.0),
        ),
        (
            "07_repetition",
            "Infinite repetition",
            "periodic XZ domain",
            repeated,
            (0.96, 0.78, 0.25),
            (4.4, 3.1, -5.6),
            (0.0, -0.35, 0.0),
        ),
        (
            "08_twist",
            "Twist",
            "Y-dependent inverse rotation",
            twisted,
            (0.4, 0.62, 1.0),
            (4.3, 2.8, -5.4),
            (0.0, 0.0, 0.0),
        ),
        (
            "09_bend",
            "Bend",
            "X-dependent inverse rotation",
            bent,
            (1.0, 0.48, 0.32),
            (4.5, 3.1, -5.8),
            (0.0, 0.15, 0.0),
        ),
        (
            "10_composition",
            "Nested composition",
            "elongate + twist + smooth CSG",
            composition,
            (0.68, 0.42, 1.0),
            (4.2, 2.9, -5.5),
            (0.0, 0.0, 0.0),
        ),
    ]

    for specification in specifications:
        set_color(specification[3], specification[4])

    return specifications


def raymarch(ray_origin, ray_direction, objects):
    distance_traveled = 0.0

    for step in range(MAX_STEPS):
        position = add(ray_origin, multiply(ray_direction, distance_traveled))
        point = as_vector3(position)
        distances = [sdf.distance(point) for sdf in objects]
        nearest_index = min(range(len(distances)), key=distances.__getitem__)
        nearest_distance = distances[nearest_index]

        if abs(nearest_distance) < EPSILON:
            return position, nearest_index, step, distance_traveled

        distance_traveled += max(abs(nearest_distance) * STEP_SAFETY, EPSILON * 0.5)
        if distance_traveled > MAX_DISTANCE:
            break

    return None


def background_color(y, height, ray_direction):
    horizon = max(0.0, min(1.0, 0.5 + ray_direction[1] * 0.75))
    vertical = y / max(height - 1, 1)
    glow = (1.0 - vertical) * 0.035
    return (
        0.025 + 0.052 * horizon + glow,
        0.035 + 0.066 * horizon + glow,
        0.073 + 0.115 * horizon + glow,
    )


def shade(hit, ray_direction, sdf, is_ground, step, distance_traveled):
    point = as_vector3(hit)
    normal_vector = SDFUtils.get_normal(sdf.distance, point, epsilon=0.002)
    normal = (normal_vector.x, normal_vector.y, normal_vector.z)
    light_direction = normalize((-0.55, 0.82, -0.42))
    fill_direction = normalize((0.65, 0.22, -0.30))
    view_direction = multiply(ray_direction, -1.0)

    diffuse = max(0.0, dot(normal, light_direction))
    fill = max(0.0, dot(normal, fill_direction))
    half_vector = normalize(add(light_direction, view_direction))
    specular = max(0.0, dot(normal, half_vector)) ** 48
    rim = (1.0 - max(0.0, dot(normal, view_direction))) ** 2.2

    if is_ground:
        checker = (math.floor(hit[0] * 1.25) + math.floor(hit[2] * 1.25)) % 2
        base = (0.105, 0.12, 0.17) if checker else (0.165, 0.185, 0.24)
        illumination = 0.43 + 0.40 * diffuse + 0.08 * fill
        color = tuple(component * illumination for component in base)
    else:
        base = (sdf.color.r, sdf.color.g, sdf.color.b)
        illumination = 0.18 + 0.72 * diffuse + 0.13 * fill
        step_tint = min(step / MAX_STEPS, 1.0) * 0.08
        color = tuple(
            component * illumination
            + component * rim * 0.18
            + specular * 0.38
            + step_tint * 0.04
            for component in base
        )

    fog = min(max((distance_traveled - 5.5) / 13.0, 0.0), 0.55)
    fog_color = (0.055, 0.065, 0.105)
    color = tuple(
        component * (1.0 - fog) + fog_component * fog
        for component, fog_component in zip(color, fog_color)
    )

    return tuple(
        int(255 * max(0.0, min(1.0, component)) ** (1.0 / 2.2))
        for component in color
    )


def render_example(sdf, width, height, camera_origin, camera_target):
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    ground = set_color(
        SDFPlane(Vector3.up(), offset=-1.15),
        (0.16, 0.18, 0.23),
    )
    objects = [sdf, ground]

    camera_forward = normalize(subtract(camera_target, camera_origin))
    camera_right = normalize(cross(camera_forward, (0.0, 1.0, 0.0)))
    camera_up = normalize(cross(camera_right, camera_forward))
    view_scale = math.tan(math.radians(42.0) * 0.5)
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

            hit, object_index, step, distance_traveled = result
            pixels[x, y] = shade(
                hit,
                ray_direction,
                objects[object_index],
                object_index == 1,
                step,
                distance_traveled,
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


def compose_contact_sheet(rendered, width, height):
    columns = 5
    rows = 2
    gap = 14
    margin = 24
    header = 76
    caption = 48
    sheet_width = margin * 2 + columns * width + (columns - 1) * gap
    sheet_height = margin * 2 + header + rows * (height + caption) + (rows - 1) * gap
    sheet = Image.new("RGB", (sheet_width, sheet_height), (11, 14, 25))
    draw = ImageDraw.Draw(sheet)
    title_font = load_font(26, bold=True)
    subtitle_font = load_font(12)
    label_font = load_font(14, bold=True)
    detail_font = load_font(10)

    draw.text((margin, margin), "Miru Expanded SDF Operations", font=title_font, fill=(240, 245, 255))
    draw.text(
        (margin, margin + 38),
        "Boolean fields • distance modifiers • inverse domain transformations",
        font=subtitle_font,
        fill=(139, 158, 196),
    )

    for index, (specification, image) in enumerate(rendered):
        _, label, detail, sdf, _, _, _ = specification
        column = index % columns
        row = index // columns
        left = margin + column * (width + gap)
        top = margin + header + row * (height + caption + gap)
        sheet.paste(image, (left, top))
        accent = (
            int(sdf.color.r * 255),
            int(sdf.color.g * 255),
            int(sdf.color.b * 255),
        )
        caption_top = top + height
        draw.rectangle((left, caption_top, left + width, caption_top + caption), fill=(24, 29, 47))
        draw.rectangle((left + 10, caption_top + 9, left + 15, caption_top + 37), fill=accent)
        draw.text((left + 24, caption_top + 6), label, font=label_font, fill=(237, 242, 255))
        draw.text((left + 24, caption_top + 27), detail, font=detail_font, fill=(131, 148, 184))

    return sheet


def render_specification(arguments):
    index, width, height = arguments
    specification = create_examples()[index]
    _, _, _, sdf, _, camera_origin, camera_target = specification
    return index, render_example(
        sdf,
        width,
        height,
        camera_origin,
        camera_target,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory", type=Path)
    parser.add_argument("--width", type=int, default=240)
    parser.add_argument("--height", type=int, default=180)
    parser.add_argument(
        "--jobs",
        type=int,
        default=min(5, os.cpu_count() or 1),
        help="Number of example images to render concurrently",
    )
    args = parser.parse_args()

    args.output_directory.mkdir(parents=True, exist_ok=True)
    specifications = create_examples()
    rendered = []
    work = [
        (index, args.width, args.height)
        for index in range(len(specifications))
    ]
    context = multiprocessing.get_context("spawn")
    with context.Pool(processes=max(1, args.jobs)) as pool:
        results = pool.map(render_specification, work)

    for index, image in results:
        specification = specifications[index]
        filename, label, _, _, _, _, _ = specification
        output = args.output_directory / f"{filename}.png"
        image.save(output)
        rendered.append((specification, image))
        print(f"Rendered {label}: {output}", flush=True)

    gallery = compose_contact_sheet(rendered, args.width, args.height)
    gallery_path = args.output_directory / "sdf_operations_gallery.png"
    gallery.save(gallery_path)
    print(f"Rendered {len(rendered)} examples and gallery to {args.output_directory}")


if __name__ == "__main__":
    main()
