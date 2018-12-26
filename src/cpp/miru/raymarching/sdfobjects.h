#include "miru/engine/vector.h"

class SceneObject;
class Transform;
class Material;
class Color;

class SDFObject : public SceneObject
{
public:
    SDFObject();

    virtual float distance(Vector3f position);
    virtual Color render(Vector3f position);

    Transform* transform;
    Material* material;
};

class SDFSphere : public SDFObject
{
public:
    SDFSphere() : SDFObject() {}

    virtual float distance(Vector3f position) override;

    float radius;
};