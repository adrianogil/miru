from scene import Scene
from camera import Camera

from sphere import Sphere
from plane import Plane
from cube import Cube

from vector import Vector3

import random
import os

try:
    range = xrange
except NameError:
    pass

total_sphere = random.randint(1,10)

scene_test = Scene()

cube = Cube(Vector3(1,0,0), Vector3(0,1.1,0),Vector3(0,0,1))
cube.transform.position = Vector3(0,0,0)
cube.transform.rotation = Vector3(10.0, 20.0, 60.0)
scene_test.add_objects(cube)

# v1 = Vector3(-1,-1, 4)
# v2 = Vector3(-1, 1, 4)
# v3 = Vector3( 1, 1, 4)
# v4 = Vector3( 1,-1, 4)
# v5 = Vector3(-2, 0, 4)
# v6 = Vector3( 2, 0, 4)

# plane1 = Plane([v1,v2,v3,v4])
# scene_test.add_objects(plane1)

# for i in range(0, total_sphere):
#     s = Sphere(random.randint(10,200) / 100.0)
#     s.transform.position = Vector3(random.randint(-3,3),random.randint(-3,3),random.randint(2,10))
#     s.albedo = (random.randint(20,255), random.randint(20,255), random.randint(20,255))
#     scene_test.add_objects(s)

# s2 = Sphere(1.6)
# s2.transform.position = Vector3(0,1,4)
# s2.albedo = (0,0,255)
# scene_test.add_objects(s2)

c = Camera()
c.fov = 90

scene_test.set_camera(c)

if os.path.exists("/sdcard/Raytracing/"):
    render_image = "/sdcard/Raytracing/test.jpg"
else:
    render_image = 'test.jpg'

scene_test.render(30, 30, render_image)
print('Scene rasterized in image path: %s' % (render_image,))