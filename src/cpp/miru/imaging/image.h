// Forward Declaration
struct ImageData;
class Color;

class Image
{
public:
    Image(int width, int height);

    int getWidth() { return this->mWidth; }
    int getHeight() { return this->mHeight; }

    void setPixel(int x, int y, const Color& color);
    void saveAsPNG(const char* filename);
private:
    int mWidth;
    int mHeight;

    ImageData* mImageData;
};

void sample_image_generation_for_dependency_test();