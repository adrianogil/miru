#include "miru/basic/definitions.h"

// Forward Declaration
class SceneObject;
class SceneRender;
class Color;
class Light;

struct SceneGraph
{
    SceneObject* object;
    SceneGraph* nextObject;
};

class Scene
{
public:
    Scene();
    void addObject(SceneObject *obj);

    SceneGraph* GetObjectList() const { return mObjectList; }

    SceneRender *renderMethod;
    Color backgroundColor;

    // Fow now, there is one light for each scene
    Light* light = NULL;
private:
    SceneGraph *mObjectList;
};