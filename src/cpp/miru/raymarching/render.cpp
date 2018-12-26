#include "miru/engine/vector.h"
#include "miru/engine/color.h"
#include "miru/engine/scene.h"
#include "miru/engine/scenerender.h"

#include "miru/raymarching/render.h"

#include <cmath>

#define MIN_MARCHING_DISTANCE 0.06
#define MAX_MARCHING_STEPS 100

void RaymarchingRender::setupFrame(const Scene* scene, const Camera *camera, uint32_t targetRenderWidth, 
                    uint32_t targetRenderHeight)
{
    SceneRender::setupFrame(scene, camera, targetRenderWidth, targetRenderHeight);
    mTargetCamera = camera;
}

Color RaymarchingRender::render(const Scene* scene, uint32_t x, uint32_t y)
{
    SceneGraph* currentObjNode = scene->GetObjectList();

    Color pixelColor = scene->backgroundColor;

    float minDistance = 1000000;
    float distance = 0;

    float pixelWidth = (float) mTargetRenderWidth;
    float pixelHeight = (float) mTargetRenderHeight;

    int findSurface = 0;

    Vector3f rightViewDirection = mTargetCamera->transform()->right();
    Vector3f upViewDirection = mTargetCamera->transform()->up();

    Vector3f nearPlanePos = mTargetCamera->transform()->position() + 
        mTargetCamera->transform()->forward() * mTargetCamera->near;

    float heightSize = 2.0 * mTargetCamera->near * tan2(mTargetCamera->fov * 0.5 * 3.14 / 180);
    float widthSize = (pixelWidth * 1.0 / pixelHeight) * heightSize;

    Vector3f pixelPos = rightViewDirection * ((x - 0.5 * pixelWidth)/pixelWidth) * widthSize;
    pixelPos = pixelPos + upViewDirection * (-1) * ((y - 0.5 * pixelHeight)/pixelHeight) * heightSize;
    pixelPos = pixelPos + nearPlanePos;

    Vector3f viewDirection = (pixelPos - mTargetCamera->position()).normalized();

    for (uint s = 0; s < MAX_MARCHING_STEPS && findSurface == 0; s++)
    {
        currentObjNode = scene->GetObjectList();

        while(currentObjNode != NULL)
        {
            SDFObject *sdfObject = (SDFObject*) currentObjNode->object;
            if (sdfObject != 0)
            {
                distance = sdfObject->distance()
            }
            currentObjNode = currentObjNode->nextObject;
        }
    }
    

    return pixelColor;
} 