template <typename T>
class Matrix44
{
public:
    Matrix44() {}
    Matrix44(const Matrix44& nm) 
    {
        for (uint8_t i = 0; i < 4; i++)
        {
            for (uint8_t j = 0; j < 4; j++)
            {
                this->m[i][j] = nm[i][j];
            }
        }
           
    }
    const T* operator[] (uint8_t i) const { return m[i]; }
    T* operator [] (uint8_t i) { return m[i]; }
    Matrix44 operator + (const Matrix44& rhs) const
    {
        Matrix44 mult;

        for (uint8_t i = 0; i < 4; i++)
        {
            for (uint8_t j = 0; j < 4; j++)
            {
                mult[i][j] = m[i][j] + rhs[i][j];
            }
        }

        return mult;
    }
    Matrix44 operator * (const Matrix44& rhs) const
    {
        Matrix44 mult;

        for (uint8_t i = 0; i < 4; i++)
        {
            for (uint8_t j = 0; j < 4; j++)
            {
                mult[i][j] = m[i][0] * rhs[0][j] + 
                             m[i][1] * rhs[1][j] + 
                             m[i][2] * rhs[2][j] + 
                             m[i][3] * rhs[3][j];
            }
        }

        return mult;
    }
    Matrix44 operator * (const T& factor) const
    {
        Matrix44 mult;

        for (uint8_t i = 0; i < 4; i++)
        {
            for (uint8_t j = 0; j < 4; j++)
            {
                mult[i][j] = m[i][j] * factor;
            }
        }

        return mult;
    }

    Matrix44 transpose()
    {
        Matrix44 newmatrix;

        for (uint8_t i = 0; i < 4; i++)
        {
            for (uint8_t j = 0; j < 4; j++)
            {
                newmatrix[j][i] = m[i][j];
            }
        }

        return newmatrix;
    }

    // Initialize the coefficient of the matrix with the coefficients of the identity matrix
    T m[4][4] =
        {{1,0,0,0},
         {0,1,0,0},
         {0,0,1,0},
         {0,0,0,1}};
};

typedef Matrix44<float> Matrix44f;

std::ostream& operator<<(std::ostream &strm, const Matrix44f &v);