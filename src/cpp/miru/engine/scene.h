#include "miru/basic/definitions.h"

// Forward Declaration
struct SceneGraph;
class SceneObject;
class SceneRender;
class Color;

class Scene
{
public:
    Scene();
    void addObject(SceneObject *obj);
    void render(const char *filename) const;

    SceneRender *renderMethod;
    Color backgroundColor;

    uint32_t targetRenderWidth = 1024;
    uint32_t targetRenderHeight = 1024;
private:
    SceneGraph *mObjectList;
};