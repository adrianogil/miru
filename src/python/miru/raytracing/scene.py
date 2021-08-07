from PIL import Image
from .ray import Ray

import numpy as np

from miru.engine.camera import Camera
from miru.engine.vector import Vector3
from miru.engine.color import Color

from miru.engine.sceneparser import SceneParser

from miru.engine.material import Material

from miru.raytracing.cube import Cube
from miru.raytracing.sphere import Sphere

try:
    range = xrange
except NameError:
    pass

class RenderData:
    def __init__(self):
        self.img = None
        self.pixel_width = 0
        self.pixel_height = 0
        self.pixels = []

class Scene:
    def __init__(self):
        self.objects = []
        self.post_processing_effects = []
        self.background_color = Color(0.0, 0.0, 0.0, 1.0)
        self.light = None
        self.ssaa_level = 1

        self.render_height = 50
        self.render_width = 50

        self.target_image_file = "test.jpg"

    def add_objects(self, obj):
        self.objects.append(obj)

    def add_post_processing(self, effect):
        self.post_processing_effects.append(effect)

    def set_ssaa(self, level):
        self.ssaa_level = level;

    def set_camera(self, camera):
        self.camera = camera

    def set_light(self, light_obj):
        self.light = light_obj

    def get_light(self):
        return self.light

    def raytracing(self, pixel_pos):
        ray = Ray(self.camera.transform.position, pixel_pos)

        pixel_color = self.background_color

        min_depth_distance = self.camera.far

        camera_pos = self.camera.transform.position

        for o in self.objects:
            intersection = o.intercepts(ray)

            if intersection['result']:
                hit_point = intersection['hit_point']
                distance_vector = hit_point.minus(camera_pos)
                depth_distance = distance_vector.magnitude()
                if depth_distance < min_depth_distance:
                    pixel_color = o.render(self, intersection)
                    min_depth_distance = depth_distance

        return pixel_color

    def render(self, pixel_height=-1, pixel_width=-1, image_file=""):

        if pixel_height > 0:
            target_pixel_height = pixel_height
        else:
            target_pixel_height = self.render_height

        if pixel_width > 0:
            target_pixel_width = pixel_width
        else:
            target_pixel_width = self.render_width

        if not image_file:
            image_file = self.target_image_file

        ssaa_render_data = RenderData()
        ssaa_render_data.pixel_height = self.ssaa_level * pixel_height
        ssaa_render_data.pixel_width = self.ssaa_level * pixel_width

        pixel_height = self.ssaa_level * target_pixel_height
        pixel_width = self.ssaa_level * target_pixel_width

        nearplane_pos = self.camera.transform.position.add(self.camera.transform.forward.multiply(self.camera.near))
        height_size = 2 * self.camera.near * np.tan(self.camera.fov * 0.5 * np.pi / 180)
        width_size = (pixel_width*1.0/pixel_height) * height_size

        # PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
        ssaa_render_data.img = Image.new( 'RGB', (pixel_width, pixel_height), "black") # create a new black image
        ssaa_render_data.pixels = ssaa_render_data.img.load() # create the pixel map

        for o in self.objects:
            o.pre_render()

        for x in range(0, pixel_width):
            for y in range(0, pixel_height):

                # World position of target pixel  in near plane
                pixel_pos =  self.camera.transform.right.multiply(((x - 0.5 * pixel_width)/(pixel_width) * width_size))\
                    .add(self.camera.transform.up.multiply((-1) * (y - 0.5*pixel_height)/(pixel_height) * height_size))\
                    .add(nearplane_pos)

                pixel_color = self.raytracing(pixel_pos)

                ssaa_render_data.pixels[x,y] = pixel_color.to_tuple(3)

        for post_fx in self.post_processing_effects:
            post_fx.apply_effect(ssaa_render_data)

        if self.ssaa_level > 1:
            render_data = RenderData()
            render_data.pixel_height = target_pixel_height
            render_data.pixel_width = target_pixel_width

            # PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
            render_data.img = Image.new( 'RGB', (target_pixel_width, target_pixel_height), "black") # create a new black image
            render_data.pixels = render_data.img.load() # create the pixel map

            ssaa_factor = 1.0/(self.ssaa_level*self.ssaa_level)

            for x in range(0, target_pixel_width):
                for y in range(0, target_pixel_height):

                    colors = [0,0,0]

                    for c in range(0, 3):

                        sum_values = 0
                        total_values = 0

                        for fx in range(0, self.ssaa_level):
                            for fy in range(0, self.ssaa_level):
                                ix = int(x*self.ssaa_level + fx - 0.5*self.ssaa_level)
                                iy = int(y*self.ssaa_level + fy - 0.5*self.ssaa_level)

                                if ix >= 0 and ix < ssaa_render_data.pixel_width and \
                                   iy >= 0 and iy < ssaa_render_data.pixel_height:

                                   sum_values = sum_values + ssaa_render_data.pixels[ix,iy][c]
                                   total_values =  total_values + 1

                        # print(sum_values)
                        colors[c] = int(sum_values*1.0/total_values)

                    # print(colors)
                    render_data.pixels[x,y] = tuple(colors)
        else:
            render_data = ssaa_render_data

        if image_file == '':
            return np.ndarray(render_data.pixels)

        render_data.img.save(image_file)

def render_scene(target_scene_file, target_image_file=None):
    print('Parsing file %s' % (target_scene_file))
    objs = {
        "cube": Cube.parse,
        "sphere": Sphere.parse,
        "camera": Camera.parse
    }
    target_scene = Scene()
    parser = SceneParser(objs)
    parser.parse(target_scene_file, target_scene)

    target_scene.render(image_file=target_image_file)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target_scene_file = sys.argv[1]
        target_image_file = None

        if len(sys.argv) > 2:
            target_image_file = sys.argv[2]
        render_scene(target_scene_file, target_image_file)

