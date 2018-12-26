#include "miru/imaging/image.h"
#include "miru/engine/color.h"
#include <stdint.h>

Image::Image(uint32_t width, uint32_t height)
{
    this->mWidth = width;
    this->mHeight = height;

    this->mImageData = new png::image< png::rgb_pixel >((png::uint_32) this->mWidth, (png::uint_32)this->mHeight);
}

void Image::setPixel(uint32_t x, uint32_t y, const Color& color)
{
    png::uint_32 px = (png::uint_32) x;
    png::uint_32 py = (png::uint_32) y;
    this->mImageData->set_pixel(px,py,png::rgb_pixel((png::byte)color.ru(), (png::byte)color.gu(), (png::byte)color.bu()));
}

void Image::saveAsPNG(const char *filename)
{
    this->mImageData->write(filename);
}

void sample_image_generation_for_dependency_test()
{
    int image_width = 1024;
    int image_height = 1024;

    //... Added sample from http://www.nongnu.org/pngpp/doc/0.2.9/
    png::image< png::rgb_pixel > image(image_width, image_height);
    for (png::uint_32 y = 0; y < image.get_height(); ++y)
    {
        for (png::uint_32 x = 0; x < image.get_width(); ++x)
        {
            image[y][x] = png::rgb_pixel(x/8, y/8, (x + y)/8);
            // non-checking equivalent of image.set_pixel(x, y, ...);
        }
    }
    image.write("rgb.png");
}