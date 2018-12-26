#include "miru/engine/vector.h"

class Transform
{
public:
    Transform();

    Vector3f position();

    Vector3f right() const { return mRight; }
    Vector3f left() const { return mLeft; }
    Vector3f up() const { return mUp; }
    Vector3f down() const { return mDown; }
    Vector3f forward() const { return mForward; }
    Vector3f backwards() const { return mBackwards; }

    Vector3f localPosition;
private:
    Vector3f mRight, mLeft, mUp, mDown, mForward, mBackwards;
};