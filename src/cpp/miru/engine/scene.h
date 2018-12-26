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
    void render(const char *filename) const;

    SceneGraph* GetObjectList() { return mObjectList; }

    SceneRender *renderMethod;
    Color backgroundColor;

    uint32_t targetRenderWidth = 1024;
    uint32_t targetRenderHeight = 1024;
private:
    SceneGraph *mObjectList;
};