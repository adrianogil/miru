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

from texture import Texture

from material import Material
from shader_lambertiantint import LambertianTintShader

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

lambertianTintMaterial = Material()
lambertianTintMaterial.albedo = Color(0.5, 0.5, 1.0, 1.0)
lambertianTintMaterial.shader = LambertianTintShader()

s1 = Sphere(0.6)
s1.transform.position = Vector3(0, 2.4, 4)
s1.material = lambertianTintMaterial
scene_test.add_objects(s1)

s2 = Sphere(1.2)
s2.transform.position = Vector3(-0.2, -2.4, 4)
s2.material = lambertianTintMaterial.clone()
s2.material.set_texture(Texture("images/moon.jpg"))
scene_test.add_objects(s2)

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

# blur_kernel = np.matrix([[0.0625, 0.125, 0.0625],
#                          [0.125,  0.25,   0.125],
#                          [0.0625, 0.125, 0.0625]])
# sharpen_kernel = np.matrix([[ 0, -1,  0],
#                             [-1,  5, -1],
#                             [ 0, -1,  0]])
# unsharp_kernel = (-1.0/256)* np.matrix([[ 1,  4,    6,  4, 1],
#                                         [ 4, 16,   24, 16, 4],
#                                         [ 6, 24, -476, 24, 6],
#                                         [ 4, 16,   24, 16, 4],
#                                         [ 1,  4,    6,  4, 1]])
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
    render_image = 'test_texture'

render_extension = '.jpg'

render_sizex = 250
render_sizey = 250

scene_test.render(render_sizex, render_sizey, render_image+ '_ssaa1' + render_extension)
scene_test.set_ssaa(2)
scene_test.render(render_sizex, render_sizey, render_image + '_ssaa2' + render_extension)
scene_test.set_ssaa(3)
scene_test.render(render_sizex, render_sizey, render_image + '_ssaa3' + render_extension)
scene_test.set_ssaa(4)
scene_test.render(render_sizex, render_sizey, render_image + '_ssaa4' + render_extension)

print('Scene rasterized in image path: %s' % (render_image,))