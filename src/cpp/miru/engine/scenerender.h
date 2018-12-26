// Forward Declaration
class Scene;
class Color;

class SceneRender
{   
public:
    SceneRender() {}
    virtual Color render(const Scene* scene, uint32_t x, uint32_t y);
};