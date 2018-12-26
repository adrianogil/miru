#include <string> 
#include <png++/png.hpp>

// Forward Declaration
class Color;

class Image
{
public:
    Image(uint32_t width, uint32_t height);

    uint32_t getWidth() { return this->mWidth; }
    uint32_t getHeight() { return this->mHeight; }

    void setPixel(uint32_t x, uint32_t y, const Color& color);
    void saveAsPNG(const char* filename);
private:
    uint32_t mWidth;
    uint32_t mHeight;

    png::image< png::rgb_pixel > *mImageData;
};

void sample_image_generation_for_dependency_test();