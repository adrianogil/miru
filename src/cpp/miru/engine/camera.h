#include "miru/basic/definitions.h"
#include "miru/engine/sceneobject.h"

// Forward Declaration
class SceneObject;

class Camera : public SceneObject
{
public:
    Camera();
    Camera(Camera &camera);

    void render(Scene* scene, 
                    uint32_t targetRenderWidth, 
                    uint32_t targetRenderHeight, 
                    const char* targetRenderFile);
    float near, far, fov;
};