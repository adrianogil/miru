#ifndef COLOR_INCLUDED
#define COLOR_INCLUDED

#include "miru/basic/definitions.h"
#include "miru/engine/vector.h"

class Color
{
public:
    Color();
    // Color(uint32_t r, uint32_t g, uint32_t b, uint32_t a);
    Color(float r, float g, float b, float a);

    Color clone()
    {
        return Color(this->r, this->g, this->b, this->a);
    }

    Vector3f toRGB()
    {
        return Vector3f(this->r, this->g, this->b);
    }

    void SetRGB(Vector3f rgb)
    {
        this->r = rgb.x;
        this->g = rgb.y;
        this->b = rgb.z;
    }

    int ru() const;
    int gu() const;
    int bu() const;
    int au() const;
private:
    float r,g,b,a;
};

#endif