#include "miru/basic/definitions.h"

// Forward Declaration
class SceneObject;
class SceneRender;
class Color;

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
private:
    SceneGraph *mObjectList;
};