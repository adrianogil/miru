from miru.raymarching.scene import Scene
from miru.raymarching.sdfcube import SDFCube

from miru.engine.camera import Camera
from miru.engine.vector import Vector3

import os

scene = Scene()

c = Camera()
c.fov = 90
scene.set_camera(c)

cube = SDFCube(Vector3(2, 2, 1))
cube.transform.position = Vector3(0.0, 0.0, 4.0)

scene.add_objects(cube)

if os.path.exists("/sdcard/Raytracing/"):
    render_image = "/sdcard/Raytracing/test"
else:
    render_image = 'test'

render_extension = '.jpg'

render_sizex = 50
render_sizey = 50

scene.render(render_sizex, render_sizey, render_image + render_extension)
