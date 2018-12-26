#include <stdint.h>

class Color
{
public:
    Color();
    // Color(uint32_t r, uint32_t g, uint32_t b, uint32_t a);
    Color(float r, float g, float b, float a);

    int ru() const;
    int gu() const;
    int bu() const;
    int au() const;
private:
    float r,g,b,a;
};