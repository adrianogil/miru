#include "miru/engine/vector.h"
#include "miru/engine/sceneobject.h"

class Material;
class Color;

class SDFObject : public SceneObject
{
public:
    SDFObject();

    virtual float distance(Vector3f position);
    virtual Color render(Vector3f position);
    Vector3f getNormalAt(Vector3f position);

    Material* material;
};

class SDFSphere : public SDFObject
{
public:
    SDFSphere() : SDFObject() {}

    virtual float distance(Vector3f position) override;

    float radius;
};