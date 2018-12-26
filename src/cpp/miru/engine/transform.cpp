#include "miru/engine/vector.h"
#include "miru/engine/transform.h"

Transform::Transform()
{
    this->localPosition = Vector3f::zero();

     this->mRight = Vector3f(1.0, 0.0, 0.0);
     this->mLeft = Vector3f(-1.0, 0.0, 0.0);
     this->mUp = Vector3f(0.0, 1.0, 0.0);
     this->mDown = Vector3f(0.0, -1.0, 0.0);
     this->mForward = Vector3f(0.0, 0.0, 1.0);
     this->mBackwards = Vector3f(0.0, 0.0, -1.0);
}

Vector3f Transform::position()
{
    return this->localPosition;
}