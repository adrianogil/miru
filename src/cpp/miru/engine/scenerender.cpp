#include "miru/engine/scenerender.h"
#include "miru/engine/sceneobject.h"
#include "miru/engine/color.h"
#include "miru/engine/scene.h"
#include "miru/engine/camera.h"

void SceneRender::setupFrame(const Scene* scene, Camera &camera, uint32_t targetRenderWidth, 
                    uint32_t targetRenderHeight)
{
    mTargetRenderWidth = targetRenderWidth;
    mTargetRenderHeight = targetRenderHeight;
}

Color SceneRender::render(const Scene* scene, uint32_t x, uint32_t y)
{ 
    return Color(1.0, 1.0, 1.0, 1.0);
}