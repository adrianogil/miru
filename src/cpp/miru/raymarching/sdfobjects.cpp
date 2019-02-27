#include "miru/raymarching/sdfobjects.h"

#include "miru/engine/color.h"
#include "miru/engine/transform.h"
#include "miru/engine/material.h"

#include <cmath>

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

Vector3f SDFObject::getNormalAt(Vector3f position)
{
    float eps = 0.01;

    Vector3f epsX = Vector3f(eps, 0.0, 0.0);
    float normalX = distance(position + epsX);
    normalX = normalX - distance(position - epsX);

    Vector3f epsY = Vector3f(0.0, eps, 0.0);
    float normalY = distance(position + epsY);
    normalY = normalY - distance(position - epsY);

    Vector3f epsZ = Vector3f(0.0, 0.0, eps);
    float normalZ = distance(position + epsZ);
    normalZ = normalZ - distance(position - epsZ);

    return Vector3f(normalX, normalY, normalZ).normalized();
}

float SDFSphere::distance(Vector3f position)
{
    return (position - transform()->position()).magnitude() - this->radius;
}

float SDFCube::distance(Vector3f position)
{
    float x = fmax(
            position.x - this->mTransform->position().x - this->size.x / 2.0,
            this->mTransform->position().x - position.x - this->size.x / 2.0
            );

    float y = fmax(
            position.y - this->mTransform->position().y - this->size.y / 2.0,
            this->mTransform->position().y - position.y - this->size.y / 2.0
            );

    float z = fmax(
            position.z - this->mTransform->position().z - this->size.z / 2.0,
            this->mTransform->position().z - position.z - this->size.z / 2.0
            );

    float d = fmax(x, y);
    d = fmax(d, z);

    return d;
}