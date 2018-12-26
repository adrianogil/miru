#include "miru/engine/color.h"
#include "miru/engine/scene.h"
#include "miru/engine/scenerender.h"

#include "miru/raymarching/render.h"

#define MIN_MARCHING_DISTANCE 0.06
#define MAX_MARCHING_STEPS 100

Color RaymarchingRender::render(const Scene* scene, uint32_t x, uint32_t y)
{
    SceneGraph* currentObjNode = scene->GetObjectList();

    Color pixelColor = scene->backgroundColor;

    float minDistance = 1000000;
    float distance = 0;

    uint findSurface = 0;

    for (uint s = 0; s < MAX_MARCHING_STEPS && findSurface == 0; s++)
    {
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