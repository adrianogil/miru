#include "miru/basic/definitions.h"
#include "miru/engine/sceneobject.h"

// Forward Declaration
class Color;

class Light : public SceneObject
{
public:
    Light();

    Color color;
    float intensity;
};