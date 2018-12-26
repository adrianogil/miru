#include "miru/basic/definitions.h"

// Forward Declaration
class Color;
class Scene;
class SceneRender;

class RaymarchingRender : public SceneRender
{
public:
    RaymarchingRender() : SceneRender() {}
    virtual Color render(const Scene *scene, uint32_t x, uint32_t y) override;
};