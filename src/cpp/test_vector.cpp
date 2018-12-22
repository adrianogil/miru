#include "vector.h"

using namespace std;

void printVector(Vector3f &a)
{
    cout << "Vector (" 
         << a.x << ", " 
         << a.y << ", " 
         << a.z << ")" << endl;
}

int main()
{
    Vector3f a;

    a.x = 2.0;
    a.y = 3.1;
    a.z = 5.2;

    Vector3f b(2.0, 3.2, 5.3);
    Vector3f c(0.0, 9.7, 0.25);

    cout << "Test:" << endl;
    printVector(a);
    printVector(b);
    cout << c << endl;
    cout << a + b << endl;
    cout << b - a << endl;
    cout << Vector3f::one().multiply(3.2) << endl;

    return 0;
}