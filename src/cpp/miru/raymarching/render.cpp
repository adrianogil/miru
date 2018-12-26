#include "miru/engine/vector.h"
#include "miru/engine/color.h"
#include "miru/engine/transform.h"
#include "miru/engine/scene.h"
#include "miru/engine/camera.h"
#include "miru/engine/material.h"
#include "miru/engine/scenerender.h"

#include "miru/raymarching/render.h"
#include "miru/raymarching/sdfobjects.h"

#include <cmath>
#include <iostream>

using namespace std;

#define MIN_MARCHING_DISTANCE 0.06
#define MAX_MARCHING_STEPS 100

void RaymarchingRender::setupFrame(const Scene* scene, Camera &camera, uint32_t targetRenderWidth, 
                    uint32_t targetRenderHeight)
{
    SceneRender::setupFrame(scene, camera, targetRenderWidth, targetRenderHeight);
    mTargetCamera = new Camera(camera);
}

Color RaymarchingRender::render(const Scene* scene, uint32_t x, uint32_t y)
{
    SceneGraph* currentObjNode = scene->GetObjectList();

    Color pixelColor = scene->backgroundColor;

    float minDistance = 1000000;
    float distance = 0;

    float pixelWidth = (float) mTargetRenderWidth;
    float pixelHeight = (float) mTargetRenderHeight;

    // cout << pixelWidth << " , " << pixelHeight << endl;

    int findSurface = 0;

    Vector3f rightViewDirection = mTargetCamera->transform()->right();
    Vector3f upViewDirection = mTargetCamera->transform()->up();

    Vector3f nearPlanePos = mTargetCamera->transform()->position() + 
        mTargetCamera->transform()->forward() * mTargetCamera->near;

    float heightSize = 2.0 * mTargetCamera->near * tan(mTargetCamera->fov * 0.5 * 3.14159265 / 180.0);
    float widthSize = (pixelWidth * 1.0 / pixelHeight) * heightSize;

    // cout << heightSize << " , " << widthSize << endl;

    Vector3f pixelPos = rightViewDirection * ((x - 0.5 * pixelWidth)/pixelWidth) * widthSize;
    pixelPos = pixelPos + upViewDirection * (-1) * ((y - 0.5 * pixelHeight)/pixelHeight) * heightSize;
    pixelPos = pixelPos + nearPlanePos;

    Vector3f viewDirection = (pixelPos - mTargetCamera->transform()->position()).normalized();

    Vector3f position = pixelPos;

    for (uint s = 0; s < MAX_MARCHING_STEPS && findSurface == 0; s++)
    {
        currentObjNode = scene->GetObjectList();

        while(currentObjNode != NULL)
        {
            SDFObject* sdfObject = (SDFObject*) (currentObjNode->object);
            if (sdfObject != 0)
            {
                distance = sdfObject->distance(position);

                if (distance < MIN_MARCHING_DISTANCE)
                {
                    LambertianShader* shader = (LambertianShader*) sdfObject->material->shader;

                    if (shader != 0)
                    {
                        shader->hitPointPosition = position;
                        shader->normal = sdfObject->getNormalAt(position);
                    }

                    pixelColor = sdfObject->render(position);
                    findSurface = 1;

                    return pixelColor;
                }

                if (distance < minDistance)
                {
                    minDistance = distance;
                }
            }
            currentObjNode = currentObjNode->nextObject;
        }

        position = position + (viewDirection * minDistance);
    }

    return pixelColor;
} 