#include "miru/engine/color.h"

#include "miru/engine/scene.h"
#include "miru/engine/sceneobject.h"

#include "miru/imaging/image.h"
#include "miru/basic/definitions.h"

struct SceneGraph
{
    SceneObject* object;
    SceneGraph* nextObject;
};

Scene::Scene()
{
    this->mObjectList = NULL;
}

void Scene::addObject(SceneObject* obj)
{
    if (mObjectList == NULL)
    {
        mObjectList = new SceneGraph();
        mObjectList->object = obj;
        mObjectList->nextObject = NULL;
    } else {
        SceneGraph *lastObj = mObjectList;
        while (lastObj->nextObject != NULL) lastObj = lastObj->nextObject;
        lastObj->nextObject = new SceneGraph();
        lastObj->nextObject->object = obj;
        lastObj->nextObject = NULL;
    }
}

void Scene::render(const char* targetRenderFile) const
{
    Image* rendered = new Image(targetRenderWidth, targetRenderHeight);

    for (uint32_t y = 0; y < rendered->getHeight(); ++y)
    {
        for (uint32_t x = 0; x < rendered->getWidth(); ++x)
        {
            rendered->setPixel(x, y, backgroundColor);
        }
    }
    
    rendered->saveAsPNG(targetRenderFile);

    delete(rendered);
}