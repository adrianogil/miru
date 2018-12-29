#include "lodepng/lodepng.h"
#include <iostream>

#include "miru/imaging/image.h"
#include "miru/engine/color.h"

//Example 1
//Encode from raw pixels to disk with a single function call
//The image argument has width * height RGBA pixels or width * height * 4 bytes
void encodeOneStep(const char* filename, std::vector<unsigned char>& image, unsigned width, unsigned height)
{
  //Encode the image
  unsigned error = lodepng::encode(filename, image, width, height);

  //if there's an error, display it
  if(error) std::cout << "encoder error " << error << ": "<< lodepng_error_text(error) << std::endl;
}


struct ImageData
{
    std::vector<unsigned char> image;
};

Image::Image(int width, int height)
{
    this->mWidth = width;
    this->mHeight = height;

    this->mImageData = new ImageData();
    this->mImageData->image.resize(width * height * 4); 
}


void Image::setPixel(int x, int y, const Color& color)
{
    this->mImageData->image[4 * this->mWidth * y + 4 * x + 0] = color.ru();
    this->mImageData->image[4 * this->mWidth * y + 4 * x + 1] = color.gu();
    this->mImageData->image[4 * this->mWidth * y + 4 * x + 2] = color.bu();
    this->mImageData->image[4 * this->mWidth * y + 4 * x + 3] = color.au();
}

void Image::saveAsPNG(const char *filename)
{
    encodeOneStep(filename, this->mImageData->image, this->mWidth, this->mHeight);
}

void sample_image_generation_for_dependency_test()
{
    //NOTE: this sample will overwrite the file or test.png without warning!
    const char* filename = "test.png";

    //generate some image
    unsigned width = 512, height = 512;
    std::vector<unsigned char> image;
    image.resize(width * height * 4);
    for(unsigned y = 0; y < height; y++)
        for(unsigned x = 0; x < width; x++)
        {
            image[4 * width * y + 4 * x + 0] = 255 * !(x & y);
            image[4 * width * y + 4 * x + 1] = x ^ y;
            image[4 * width * y + 4 * x + 2] = x | y;
            image[4 * width * y + 4 * x + 3] = 255;
        }

    encodeOneStep(filename, image, width, height);
}