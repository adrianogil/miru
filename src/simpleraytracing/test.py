from scene import Scene
from sphere import Sphere
from camera import Camera

s1 = Sphere(3.0)

scene_test = Scene()
scene_test.add_objects(s1)

c = Camera()

scene_test.render(100,100, 'test.jpg')