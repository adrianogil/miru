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

from material import Material
from shader_lambertiantint import LambertianTintShader

from texture import Texture

import numpy as np

import datetime

try:
    range = xrange
except NameError:
    pass



def render_random_spheres(scene):
    total_sphere = random.randint(1,15)

    light = Light(Color(1.0, 1.0, 1.0, 1.0), 1.0)
    light.transform.position = Vector3(0.0, 2.0, -2.0)
    scene.set_light(light)

    for i in range(0, total_sphere):
        s = Sphere(random.randint(10,200) / 100.0)
        s.transform.position = Vector3(random.randint(-3,3),random.randint(-3,3),random.randint(2,10))
        s.albedo = Color(float(random.randint(20,255))*1.0/255.0, float(random.randint(20,255))*1.0/255.0, float(random.randint(20,255))*1.0/255.0, 1.0)
        print("Sphere got color " + str(s.albedo))
        scene.add_objects(s)

    v1 = Vector3(8.0, 0.0, -1.0)
    v2 = Vector3(0.0, 8.0, -3.0)

    animation_velocity = 0.5

    def update_method(t):
        p = Vector3(0.0, 2.0, -2.0)
        p = p.add(v1.multiply(np.cos(animation_velocity*t*np.pi)))
        p = p.add(v2.multiply(np.sin(animation_velocity*t*np.pi)))

        light.transform.position = p

    return update_method

def render_moon(scene):

    light = Light(Color(1.0, 1.0, 1.0, 1.0), 1.0)
    light.transform.position = Vector3(0.0, 2.0, -2.0)
    scene.set_light(light)

    lambertianTintMaterial = Material()
    lambertianTintMaterial.albedo = Color(1.0, 1.0, 1.0, 1.0)
    lambertianTintMaterial.shader = LambertianTintShader()

    s1_earth = Sphere(0.6)
    s1_earth.transform.position = Vector3(0, 0, 1.5)
    s1_earth.material = lambertianTintMaterial.clone()
    scene.add_objects(s1_earth)

    s2_moon = Sphere(0.4)
    s2_moon.transform.position = Vector3(-0.2, -0.5, 1.2)
    s2_moon.material = lambertianTintMaterial.clone()
    s2_moon.material.set_texture(Texture("images/moon.jpg"))
    scene.add_objects(s2_moon)

    v1 = Vector3(0.0, 1.5, 0.5)
    v2 = Vector3(0.5, -1.0, 0.0)
    animation_velocity = 0.4

    def update_method(t):
        p = Vector3(-0.2, -0.5, 1.2)
        p = p.add(v1.multiply(np.cos(animation_velocity*t*np.pi)))
        p = p.add(v2.multiply(np.sin(animation_velocity*t*np.pi)))

        s2_moon.transform.position = p
        s2_moon.transform.rotation = Vector3(0.0, np.mod(0.5*animation_velocity*t, 360), 0.0)

    return update_method

# Render scene
#   @param total_time - Total time in seconds
def render(scene, update_method, render_sizex = 224, render_sizey = 256, \
            render_extension = '.mp4', total_time = 10.0, fps = 15):
    if os.path.exists("/sdcard/Raytracing/"):
        render_image = "/sdcard/Raytracing/test_video"
    else:
        render_image = 'rendered/test_video'

    now = datetime.datetime.now()
    render_image = render_image + now.strftime("_%Y_%m_%d_%H_%M_%S")

    delta_time = 1.0 / fps

    t = 0
    frame_count = 0

    render_image = render_image + render_extension

    with imageio.get_writer(render_image, fps=fps) as writer:
        for f in xrange(0, int(fps*total_time)):
            update_method(t)

            t = t + delta_time
            frame_count = frame_count + 1

            scene.render(render_sizex, render_sizey, 'temp/git_video_img_' + str(frame_count) + '.jpg')
            writer.append_data(imageio.imread('temp/git_video_img_' + str(frame_count) + '.jpg'))

    print('Scene rasterized in image path: %s' % (render_image,))

def render_setup():
    scene = Scene()
    c = Camera()
    c.fov = 60
    scene.set_ssaa(1)
    scene.set_camera(c)

    # update_method = render_random_spheres(scene)
    update_method = render_moon(scene)

    render(scene, update_method, total_time=5.0)

if __name__ == '__main__':
    render_setup()


