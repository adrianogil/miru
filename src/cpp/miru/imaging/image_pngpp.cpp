#include <string> 
#include <png++/png.hpp>

#include "miru/imaging/image.h"

void sample_image_generation_for_dependency_test()
{
    //... Added sample from http://www.nongnu.org/pngpp/doc/0.2.9/
    png::image< png::rgb_pixel > image(128, 128);
    for (png::uint_32 y = 0; y < image.get_height(); ++y)
    {
        for (png::uint_32 x = 0; x < image.get_width(); ++x)
        {
            image[y][x] = png::rgb_pixel(x, y, x + y);
            // non-checking equivalent of image.set_pixel(x, y, ...);
        }
    }
    image.write("rgb.png");
}