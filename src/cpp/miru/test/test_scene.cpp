#include "miru/engine/color.h"
#include "miru/engine/scene.h"

int main()
{
    Scene *scene = new Scene();

    scene->backgroundColor = Color(1.0, 1.0, 0.0, 1.0);
    const char* filename = "scene.png";
    // scene->render(filename);

    delete(scene);
}