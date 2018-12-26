#include "miru/engine/transform.h"
#include "miru/engine/sceneobject.h"

SceneObject::SceneObject()
{
    this->mTransform = new Transform();
}