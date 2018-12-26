#include "miru/engine/color.h"
#include "miru/engine/vector.h"

class Shader;
class Scene;

class Material
{
public:
    Material();

    Color render();

    Color albedo;
    Shader *shader;
};

class Shader
{
public:
    Shader() {}

    virtual Color renderFragment() { return Color(0.0, 0.0, 0.0, 1.0); }
};

class UnlitShader : public Shader
{
public:
    virtual Color renderFragment() override 
    { 
        return material->albedo;
    }

    Material *material;
};

class LambertianShader : public Shader
{
public:
    virtual Color renderFragment() override;

    Vector3f hitPointPosition;
    Scene *scene;
    Material *material;
    Vector3f normal;
};

