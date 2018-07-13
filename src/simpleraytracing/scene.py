from PIL import Image
from ray import Ray

import numpy as np

from vector import Vector3

from color import Color

try:
    range = xrange
except NameError:
    pass

class Scene:
    def __init__(self):
        self.objects = []
        self.background_color = Color(0.0,0.0,0.0,1.0)
        self.light = None

    def add_objects(self, obj):
        self.objects.append(obj)

    def set_camera(self, camera):
        self.camera = camera

    def set_light(self, light_obj):
        self.light = light_obj

    def get_light(self):
        return self.light

    def render(self, pixel_height, pixel_width, image_file):

        nearplane_pos = self.camera.transform.position.add(self.camera.transform.forward.multiply(self.camera.near))
        height_size = 2 * self.camera.near * np.tan(self.camera.fov * 0.5 * np.pi / 180)
        width_size = (pixel_width*1.0/pixel_height) * height_size

        # PIL accesses images in Cartesian co-ordinates, so it is Image[columns, rows]
        img = Image.new( 'RGB', (pixel_width, pixel_height), "black") # create a new black image
        pixels = img.load() # create the pixel map

        for o in self.objects:
            o.pre_render()

        for x in range(0, pixel_width):
            for y in range(0, pixel_height):


                # World position of target pixel  in near plane
                pixel_pos =  self.camera.transform.right.multiply(((x - 0.5 * pixel_width)/(pixel_width) * width_size))\
                    .add(self.camera.transform.up.multiply((y - 0.5*pixel_height)/(pixel_height) * height_size))\
                    .add(nearplane_pos)

                ray = Ray(self.camera.transform.position, pixel_pos)

                pixel_color = self.background_color

                obj_normal = Vector3.up()
                min_depth_distance = self.camera.far

                for o in self.objects:
                    intersection = o.intercepts(ray)
                    
                    if intersection['result']:
                        depth_distance = intersection['hit_point'].minus(self.camera.transform.position).magnitude()
                        if depth_distance < min_depth_distance:
                            pixel_color = o.render(self, intersection)
                            # import pdb; pdb.set_trace() # Start debugger
                            min_depth_distance = depth_distance

                pixels[x,y] = pixel_color.to_tuple(3)

        img.save(image_file)