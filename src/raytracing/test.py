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

# cube = Cube(Vector3(1.2,0,0), Vector3(0,1.1,0),Vector3(0,0,1.3))
# cube.transform.position = Vector3(0,0,2)
# cube.transform.rotation = Vector3(2.0, 15.0, 5.5)
# scene_test.add_objects(cube)

# v1 = Vector3(-1,-1, 4)
# v2 = Vector3(-1, 1, 4)
# v3 = Vector3( 1, 1, 4)
# v4 = Vector3( 1,-1, 4)
# v5 = Vector3(-2, 0, 4)
# v6 = Vector3( 2, 0, 4)

# plane1 = Plane([v1,v2,v3,v4])
# scene_test.add_objects(plane1)

for i in range(0, total_sphere):
    s = Sphere(random.randint(10,200) / 100.0)
    s.transform.position = Vector3(random.randint(-3,3),random.randint(-3,3),random.randint(2,10))
    s.albedo = Color(float(random.randint(20,255))*1.0/255.0, float(random.randint(20,255))*1.0/255.0, float(random.randint(20,255))*1.0/255.0, 1.0)
    print("Sphere got color " + str(s.albedo))
    scene_test.add_objects(s)

# s2 = Sphere(1.6)
# s2.transform.position = Vector3(0,1,4)
# s2.albedo = (0,0,255)
# scene_test.add_objects(s2)

# mesh = Mesh()
# mesh.vertices = [Vector3(0.0, 0.0, 2.0), Vector3(2.0, 0.0, 2.0), Vector3(1.0, 2.0, 3.0)]
# mesh.triangles = [0,1,2]
# quadmesh.create(mesh, Vector3(0.0, 0.0, 2.0), Vector3(2.0, 8.0, 2.0), Vector3(1.0, 2.0, 3.0))
# mesh.albedo = (255,255,0)
# scene_test.add_objects(mesh)

c = Camera()
c.fov = 90

scene_test.set_ssaa(1)
scene_test.set_camera(c)

blur_kernel = np.matrix([[0.0625, 0.125, 0.0625],
                         [0.125,  0.25,   0.125],
                         [0.0625, 0.125, 0.0625]])
sharpen_kernel = np.matrix([[ 0, -1,  0],
                            [-1,  5, -1],
                            [ 0, -1,  0]])
unsharp_kernel = (-1.0/256)* np.matrix([[ 1,  4,    6,  4, 1],
                                        [ 4, 16,   24, 16, 4],
                                        [ 6, 24, -476, 24, 6],
                                        [ 4, 16,   24, 16, 4],
                                        [ 1,  4,    6,  4, 1]])
# kernel = np.matrix([[],[],[]])

# scene_test.add_post_processing(KernelFilter(unsharp_kernel, 5, 5))
# scene_test.add_post_processing(KernelFilter(sharpen_kernel, 3, 3))
# scene_test.add_post_processing(MeanFilter())
# blur_kernel = np.matrix([[0.0625, 0.125, 0.0625],[0.125, 0.25, 0.125],[0.0625, 0.125, 0.0625]])
# kernel = np.matrix([[],[],[]])

# scene_test.add_post_processing(KernelFilter(blur_kernel, 3, 3))
# scene_test.add_post_processing(MeanFilter())

if os.path.exists("/sdcard/Raytracing/"):
    render_image = "/sdcard/Raytracing/test"
else:
    render_image = 'test'

render_extension = '.jpg'

render_sizex = 200
render_sizey = 200

scene_test.render(render_sizex, render_sizey, render_image + render_extension)
scene_test.set_ssaa(2)
scene_test.render(render_sizex, render_sizey, render_image + '_ssaa2' + render_extension)
scene_test.set_ssaa(3)
scene_test.render(render_sizex, render_sizey, render_image + '_ssaa3' + render_extension)
scene_test.set_ssaa(4)
scene_test.render(render_sizex, render_sizey, render_image + '_ssaa4' + render_extension)

print('Scene rasterized in image path: %s' % (render_image,))