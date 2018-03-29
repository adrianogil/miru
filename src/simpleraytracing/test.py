from scene import Scene
from sphere import Sphere
from camera import Camera

from vector import Vector3

import random

try:
    range = xrange
except NameError:
    pass

total_sphere = random.randint(1,10)

scene_test = Scene()

for i in range(0, total_sphere):
    s = Sphere(random.randint(10,100) / 100.0)
    s.transform.position = Vector3(random.randint(-3,3),random.randint(-3,3),random.randint(2,10))
    s.albedo = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    scene_test.add_objects(s)

# s2 = Sphere(1.6)
# s2.transform.position = Vector3(0,1,4)
# s2.albedo = (0,0,255)
# scene_test.add_objects(s2)
# scene_test.add_objects(s1)

c = Camera()
c.fov = 90

scene_test.set_camera(c)
scene_test.render(250,250, 'test.jpg')