#include <iostream>
#include <cmath>

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
    Vector3(const Vector3 &v) : x(v.x), y(v.y), z(v.z) {}

    Vector3 multiply(T factor)
    {
        return Vector3(this->x*factor, this->y*factor, this->z*factor);
    }

    Vector3 scale(Vector3 v)
    {
        return Vector3(this->x*v.x, this->y*v.y, this->z*v.z);
    }

    T sqrMagnitude()
    {
        return this->x*this->x + this->y*this->y + this->z*this->z;
    }

    T magnitude()
    {
        return sqrt(this->x*this->x + this->y*this->y + this->z*this->z);
    }

    Vector3 normalized()
    {
        return this->multiply(1/this->sqrMagnitude());
    }

    T dotProduct(const Vector3 &v)
    {
        return this->x * v.x + this->y * v.y + this->z * v.z;
    }

    Vector3 crossProduct(const Vector3 &v)
    {
        T new_x = this->y*v.z - this->z*v.y;
        T new_y = this->z*v.x - this->x*v.z;
        T new_z = this->x*v.y - this->y*v.x;

        return Vector3(new_x, new_y, new_z);
    }

    friend Vector3 operator+(const Vector3 &a, const Vector3 &b);
    friend Vector3 operator-(const Vector3 &a, const Vector3 &b);

    static Vector3 zero() { return Vector3(T(0), T(0), T(0)); }
    static Vector3 one() { return Vector3(T(1), T(1), T(1)); }

    T x, y, z;
};


typedef Vector3<float> Vector3f;
// Vector3f::zero = Vector3f(0,0,0);
// Vector3f::one = Vector3f(1.0, 1.0, 1.0);

Vector3f operator+(const Vector3f &a, const Vector3f &b);
Vector3f operator-(const Vector3f &a, const Vector3f &b);
std::ostream& operator<<(std::ostream &strm, const Vector3f &v);