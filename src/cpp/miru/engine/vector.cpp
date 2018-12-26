#include "vector.h"

std::ostream& operator<<(std::ostream &strm, const Vector3f &v) {
        strm << "Vector (" 
         << v.x << ", " 
         << v.y << ", " 
         << v.z << ")";

         return strm;
}

Vector3f operator+(const Vector3f &a, const Vector3f &b)
{
    return Vector3f(a.x+b.x, a.y+b.y, a.z+b.z);
}

Vector3f operator-(const Vector3f &a, const Vector3f &b)
{
    return Vector3f(a.x-b.x, a.y-b.y, a.z-b.z);
}