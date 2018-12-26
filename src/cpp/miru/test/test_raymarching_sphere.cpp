 #include "miru/engine/color.h"

#include "miru/engine/scene.h"
#include "miru/engine/scenerender.h"
#include "miru/raymarching/render.h"

 int main()
 {
    Scene *scene = new Scene();
    scene->backgroundColor = Color(1.0, 1.0, 0.0, 1.0);
    
    scene->renderMethod = new RaymarchingRender();

    // SDFSphere* sphere = new SDFSphere();
    // sphere->material->albedo = Color(1.0, 0.0, 0.0, 1.0);
    // scene->addObject(sphere);

    const char* filename = "scene.png";
    scene->render(filename);

    delete(scene);
 }