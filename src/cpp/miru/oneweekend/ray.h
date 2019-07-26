#ifndef RAYH
#define RAYH
#include "vec3.h"

class ray
{

public:
    ray() { }
    ray(const vec3& a, const vec3& b) { A = a; B = b; }
    vec3 origin() const { return A; }
    vec3 direction() const { return B; }
    vec3 point_at(float t) const { return A + t * B; }

    // Start position
    vec3 A;
    // Direction
    vec3 B;
};


#endif