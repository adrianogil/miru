#include "miru/basic/definitions.h"

// Forward Declaration
class Scene;
class Color;
class Camera;

class SceneRender
{   
public:
    SceneRender() {}
    virtual void setupFrame(const Scene* scene, const Camera *camera, uint32_t targetRenderWidth, 
                    uint32_t targetRenderHeight);
    virtual Color render(const Scene* scene, uint32_t x, uint32_t y);
protected:
    uint32_t mTargetRenderWidth;
    uint32_t mTargetRenderHeight;
};