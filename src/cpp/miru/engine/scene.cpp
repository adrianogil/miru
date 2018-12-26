#include "miru/engine/color.h"

#include "miru/engine/scene.h"
#include "miru/engine/light.h"
#include "miru/engine/scenerender.h"
#include "miru/engine/sceneobject.h"

#include "miru/imaging/image.h"
#include "miru/basic/definitions.h"

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