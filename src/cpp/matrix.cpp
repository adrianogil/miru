#include <iostream>

#include "matrix.h"

std::ostream& operator<<(std::ostream &strm, const Matrix44f &v)
{
    strm << "Matrix(\n";

    for (uint8_t i = 0; i < 4; i++)
    {
        strm << "\t";
        for (uint8_t j = 0; j < 4; j++)
        {
            strm << v[i][j] << ", ";
        }
        strm << "\n";
    }

    strm << ")";

    return strm;
}