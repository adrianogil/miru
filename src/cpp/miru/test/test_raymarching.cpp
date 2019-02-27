#include "miru/engine/color.h"
#include "miru/engine/vector.h"
#include "miru/engine/transform.h"
#include "miru/engine/sceneobject.h"
#include "miru/engine/scene.h"
#include "miru/engine/camera.h"
#include "miru/engine/light.h"

#include "miru/engine/scenerender.h"
#include "miru/raymarching/render.h"
#include "miru/raymarching/sdfobjects.h"
#include "miru/engine/material.h"

 int main()
 {
    Scene *scene = new Scene();
    scene->backgroundColor = Color(0.15, 0.05, 0.05, 1.0);
    
    scene->renderMethod = new RaymarchingRender();

    SDFCube* cube = new SDFCube();
    cube->size = Vector3f(1.2, 0.4, 0.9);
    cube->material->albedo = Color(0.2, 0.5, 0.81, 1.0);

    SDFSphere* sphere = new SDFSphere();
    sphere->radius = 1.2f;
    sphere->material->albedo = Color(1.0, 0.05, 0.01, 1.0);

    LambertianShader* lambertian = new LambertianShader();
    lambertian->material = sphere->material;
    lambertian->scene = scene;

    LambertianShader* lambertian2 = new LambertianShader();
    lambertian2->material = cube->material;
    lambertian2->scene = scene;

    sphere->material->shader = lambertian;
    // cube->material->shader = lambertian2;
    
    sphere->transform()->localPosition = Vector3f(0.2, 0.2, 4.5);
    cube->transform()->localPosition = Vector3f(-0.5, -0.2, 2.1);

    scene->addObject(sphere);
    scene->addObject(cube);

    Light* light = new Light();
    light->intensity = 1.0;
    light->color = Color(1.0, 1.0, 0.5, 1.0);
    light->transform()->localPosition = Vector3f(1.0, 5.0, -5);
    scene->light = light;

    const char* filename = "raymarching_scene.png";
    
    Camera* camera = new Camera();
    camera->near = 0.2;
    camera->far = 100;
    camera->fov = 60;

    camera->render(scene, 1024, 1024, filename);
    
    delete(scene);
    delete(light);
    delete(sphere);
    delete(cube);
 }