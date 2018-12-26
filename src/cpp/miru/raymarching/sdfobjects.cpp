#include "miru/engine/color.h"
#include "miru/engine/transform.h"
#include "miru/engine/material.h"
#include "miru/engine/sceneobject.h"
#include "miru/raymarching/sdfobjects.h"

SDFObject::SDFObject() : SceneObject()
{
    this->material = new Material();
}

float SDFObject::distance(Vector3f position)
{
    return 0.0;
}

Color SDFObject::render(Vector3f position)
{
    return this->material->render();
}

float SDFSphere::distance(Vector3f position)
{
    return (position - transform()->position()).magnitude();
}
