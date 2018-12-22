
template<typename T>

class Vector3
// Vector3 class
// Based on:
//  - https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/geometry
{
public:
    // Initializing

    Vector3() : x(T(0)), y(T(0)), z(T(0)) {}
    Vector3(const T &xx) : x(xx), y(xx), z(xx) {}
    Vector3(T xx, T yy, T zz) : x(xx), y(yy), z(zz) {}
    
    T x, y, z;
    
};


typedef Vector3<float> Vector3f;