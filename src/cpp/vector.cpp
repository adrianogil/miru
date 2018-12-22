#include "vector.h"

std::ostream& operator<<(std::ostream &strm, const Vector3f &v) {
        strm << "Vector (" 
         << v.x << ", " 
         << v.y << ", " 
         << v.z << ")";

         return strm;
}