#include "miru/engine/sceneobject.h"
#include "miru/engine/scene.h"
#include "miru/engine/scenerender.h"
#include "miru/engine/color.h"
#include "miru/engine/camera.h"

#include "miru/imaging/image.h"

Camera::Camera() : public SceneObject()
{

}

void Camera::render(Scene* scene, 
                    uint32_t targetRenderWidth, 
                    uint32_t targetRenderHeight, 
                    const char* targetRenderFile)
{
    scene->renderMethod->setupFrame(this, scene, targetRenderWidth, targetRenderHeight);

    Image* rendered = new Image(targetRenderWidth, targetRenderHeight);

    for (uint32_t y = 0; y < rendered->getHeight(); ++y)
    {
        for (uint32_t x = 0; x < rendered->getWidth(); ++x)
        {
            Color pixelColor = scene->renderMethod->render(scene, x, y);
            rendered->setPixel(x, y, pixelColor);
        }
    }
    
    rendered->saveAsPNG(targetRenderFile);

    delete(rendered);
}