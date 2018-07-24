import imageio

from scene import Scene
from camera import Camera

from sphere import Sphere
from plane import Plane
from cube import Cube

from vector import Vector3

from mesh import Mesh
import quadmesh

from light import Light

import random
import os

from color import Color

from meanfilter import MeanFilter
from kernelfilter import KernelFilter

import numpy as np

try:
    range = xrange
except NameError:
    pass

total_sphere = random.randint(1,15)

scene_test = Scene()

light = Light(Color(1.0, 1.0, 1.0, 1.0), 1.0)
light.transform.position = Vector3(0.0, 2.0, -2.0)
scene_test.set_light(light)

for i in range(0, total_sphere):
    s = Sphere(random.randint(10,200) / 100.0)
    s.transform.position = Vector3(random.randint(-3,3),random.randint(-3,3),random.randint(2,10))
    s.albedo = Color(float(random.randint(20,255))*1.0/255.0, float(random.randint(20,255))*1.0/255.0, float(random.randint(20,255))*1.0/255.0, 1.0)
    print("Sphere got color " + str(s.albedo))
    scene_test.add_objects(s)

c = Camera()
c.fov = 90
scene_test.set_ssaa(1)
scene_test.set_camera(c)

if os.path.exists("/sdcard/Raytracing/"):
    render_image = "/sdcard/Raytracing/test_video"
else:
    render_image = 'rendered/test_video'

render_extension = '.mp4'

render_sizex = 224
render_sizey = 256

total_time = 10.0 # Seconds
fps = 15 # Frames per seconds
delta_time = 1.0 / fps

t = 0
frame_count = 0

v1 = Vector3(8.0, 0.0, -1.0)
v2 = Vector3(0.0, 8.0, -3.0)

render_image = render_image + render_extension

animation_velocity = 0.5

with imageio.get_writer(render_image, fps=fps) as writer:
    for f in xrange(0, int(fps*total_time)):
        p = Vector3(0.0, 2.0, -2.0)
        p = p.add(v1.multiply(np.cos(animation_velocity*t*np.pi)))
        p = p.add(v2.multiply(np.sin(animation_velocity*t*np.pi)))
        
        light.transform.position = p
        
        t = t + delta_time
        frame_count = frame_count + 1

        scene_test.render(render_sizex, render_sizey, 'temp/git_video_img_' + str(frame_count) + '.jpg')
        writer.append_data(imageio.imread('temp/git_video_img_' + str(frame_count) + '.jpg'))

print('Scene rasterized in image path: %s' % (render_image,))