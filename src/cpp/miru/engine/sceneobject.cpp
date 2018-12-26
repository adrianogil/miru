#include "miru/engine/transform.h"
#include "miru/engine/sceneobject.h"

SceneObject::SceneObject()
{
    this->mTransform = new Transform();
}

SceneObject::SceneObject(SceneObject &object)
{
    Transform *pTransform = object.mTransform;
    this->mTransform = new Transform(*pTransform);
}

Transform* SceneObject::transform()
{
    return mTransform;
}