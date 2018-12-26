#include <iostream>

#include "miru/engine/matrix.h"

using namespace std;

int main()
{
    Matrix44f a;
    Matrix44f b = a.transpose();

    cout << a * 2.5 << endl;
    cout << b << endl;

    b[2][0] = 4.5;
    b[3][0] = 2.3;

    Matrix44f c = b.transpose();
    Matrix44f d = b*2.5 + c*4.3;

    cout << d << endl;
    cout << d * c << endl;
    cout << (d * c).transpose() << endl;
    cout << (d * c).transpose() + c * d << endl;

    return 0;
}