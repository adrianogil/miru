
class Color;

class Material
{
public:
    Material() {}

    Color render() { return albedo; }

    Color albedo;
};