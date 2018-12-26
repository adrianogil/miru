#include "miru/engine/vector.h"
#include "miru/engine/transform.h"

Transform::Transform()
{
    this->localPosition = Vector3f::zero();
}

Vector3f Transform::position()
{
    return this->localPosition;
}