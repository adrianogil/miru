#include "miru/basic/definitions.h"

// Forward Declaration
class SceneObject;

class Camera : public SceneObject
{
public:
    Camera();

    void render(Scene* scene, 
                    uint32_t targetRenderWidth, 
                    uint32_t targetRenderHeight, 
                    const char* targetRenderFile);
    float near, far, fov;
};