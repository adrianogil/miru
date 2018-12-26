#include "miru/basic/definitions.h"

// Forward Declaration
class Color;
class Scene;
class Camera;
class SceneRender;

class RaymarchingRender : public SceneRender
{
public:
    RaymarchingRender() : SceneRender() {}

    virtual void setupFrame(const Scene* scene, Camera &camera, uint32_t targetRenderWidth, uint32_t targetRenderHeight) override;
    virtual Color render(const Scene *scene, uint32_t x, uint32_t y) override;
private:
    Camera* mTargetCamera;
};