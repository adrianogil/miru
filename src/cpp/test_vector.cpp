#include <iostream>
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

    cout << "Test:" << endl;
    printVector(a);
    printVector(b);

    return 0;
}