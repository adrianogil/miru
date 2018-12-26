#include "miru/engine/color.h"
#include <stdint.h>

Color::Color()
{

    this->r = 0.0;
    this->g = 0.0;
    this->b = 0.0;
    this->a = 0.0;
}

// Color::Color(uint32_t r, uint32_t g, uint32_t b, uint32_t a)
// {   
//     this->r = r/255.0;
//     this->g = g/255.0;
//     this->b = b/255.0;
//     this->a = a/255.0;
// }

Color::Color(float r, float g, float b, float a)
{
    this->r = r;
    this->g = g;
    this->b = b;
    this->a = a;
}

int Color::ru() const
{
    return (int) (255.0 * this->r);
}

int Color::gu() const
{
    return (int) (255.0 * this->g);
}

int Color::bu() const
{
    return (int) (255.0 * this->b);
}

int Color::au() const
{
    return (int) (255.0 * this->a);
}





