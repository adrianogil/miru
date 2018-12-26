 #include "miru/engine/color.h"

#include "miru/engine/scene.h"
#include "miru/engine/sceneobject.h"
#include "miru/engine/scenerender.h"
#include "miru/raymarching/render.h"
#include "miru/raymarching/sdfobjects.h"

#include "miru/engine/camera.h"

 int main()
 {
    Scene *scene = new Scene();
    scene->backgroundColor = Color(1.0, 1.0, 0.0, 1.0);
    
    scene->renderMethod = new RaymarchingRender();

    SDFSphere* sphere = new SDFSphere();
    sphere->material->albedo = Color(1.0, 0.0, 0.0, 1.0);
    scene->addObject(sphere);

    const char* filename = "scene.png";
    
    Camera* camera = new Camera();
    camera->near = 0.2;
    camera->far = 100;
    camera->fov = 60;

    camera->render(scene, 1024, 1024, filename);
    
    delete(scene);
 }