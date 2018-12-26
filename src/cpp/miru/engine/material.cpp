#include "miru/engine/color.h"
#include "miru/engine/scene.h"
#include "miru/engine/light.h"
#include "miru/engine/material.h"
#include "miru/engine/transform.h"

#include <cmath>

Material::Material()
{
    
}

Color Material::render()
{
    if (shader != NULL)
    {
        return shader->renderFragment();
    }
    return albedo; 
}

Color LambertianShader::renderFragment()
{
    Color renderColor = material->albedo.clone();

    Vector3f lightDirection = (scene->light->transform()->position() - hitPointPosition).normalized();
    float dotNL = fmax(0.0, normal.dotProduct(lightDirection));

    Vector3f rgbValue = renderColor.toRGB() * dotNL * scene->light->intensity;
    rgbValue.scale(scene->light->color.toRGB());

    renderColor.SetRGB(rgbValue);

    return renderColor;
}