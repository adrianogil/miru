from PIL import Image
import numpy as np
import os

from engine.vector import Vector3
from engine.color import Color

from engine.camera import Camera
from engine.sceneparser import SceneParser

from sdfcube import SDFCube


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
        self.background_color = Color(0.0,0.0,0.0,1.0)
        self.light = None
        self.ssaa_level = 1
        self.min_marching_distance = 0.06
        self.max_marching_steps = 40

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

    def raymarching(self, position, view_direction):
        min_distance = 10000
        next_distance = self.min_marching_distance

        find_surface = False

        pixel_color = self.background_color

        for s in range(0, self.max_marching_steps):
            for o in self.objects:
                distance = o.distance(position)
                if distance < self.min_marching_distance:
                    pixel_color = o.render(self, position)
                    break
                if distance < min_distance:
                    min_distance = distance
            
            next_distance = min_distance

            if find_surface:
                break
            position = position.add(view_direction.multiply(next_distance))

        return pixel_color

    def render(self, pixel_height, pixel_width, image_file=""):

        target_pixel_height = pixel_height
        target_pixel_width = pixel_width

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

                position = pixel_pos
                view_direction = pixel_pos.minus(self.camera.transform.position).normalized()

                pixel_color = self.raymarching(position, view_direction)

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

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target_scene_file = sys.argv[1]
        print('Parsing file %s' % (target_scene_file))
        objs = {
            "cube"   : SDFCube.parse,
            "camera" : Camera.parse,
        }
        target_scene = Scene()
        parser = SceneParser(objs)
        parser.parse(target_scene_file, target_scene)

        if os.path.exists("/sdcard/Rendering/"):
            render_image = "/sdcard/Rendering/test"
        else:
            render_image = 'test'

        render_extension = '.jpg'

        render_sizex = 50
        render_sizey = 50

        target_scene.render(render_sizex, render_sizey, render_image + render_extension)
