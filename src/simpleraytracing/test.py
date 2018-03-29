from scene import Scene
from sphere import Sphere
from camera import Camera

from vector import Vector3

s1 = Sphere(3.0)
s1.transform.position = Vector3(0,0,5)

scene_test = Scene()
scene_test.add_objects(s1)

c = Camera()
c.fov = 90

scene_test.set_camera(c)
scene_test.render(100,100, 'test.jpg')