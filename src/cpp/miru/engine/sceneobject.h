#ifndef SCENEOBJECT_INCLUDED
#define SCENEOBJECT_INCLUDED

// Forward Declaration
class Transform;

class SceneObject
{
public:
    SceneObject();
    SceneObject(SceneObject &object);

    Transform* transform();

protected:
    Transform* mTransform;
};

#endif