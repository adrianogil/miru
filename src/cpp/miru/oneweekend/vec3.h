#ifndef VEC3H
#define VEC3H

#include <math.h>
#include "stdlib.h"
#include "iostream"

class vec3 {

public:
    vec3() {}
    vec3(float e0, float e1 , float e2) { e[0] = e0; e[1] = e1; e[2] = e2; }
    inline float x() const { return e[0]; }
    inline float y() const { return e[1]; }
    inline float z() const { return e[2]; }
    inline float r() const { return e[0]; }
    inline float g() const { return e[1]; }
    inline float b() const { return e[2]; }

    inline const vec3& operator+() const { return *this; }
    inline vec3 operator-() const { return vec3(-e[0], -e[1], -e[2]); }
    inline float operator[](int i) const { return e[i]; }
    inline float& operator[](int i) { return e[i]; };

    inline vec3& operator+=(const vec3 &v2)
    {
        e[0] += v2.e[0]; e[1] += v2.e[1]; e[2] += v2.e[2];
        return *this;
    }
    inline vec3& operator-=(const vec3 &v2);
    inline vec3& operator*=(const vec3 &v2);
    inline vec3& operator/=(const vec3 &v2);
    inline vec3& operator*=(const float t);
    inline vec3& operator/=(const float t)
    {
        e[0] /= t; e[1] /= t; e[2] /= t;
        return *this;
    }

    inline float length() const { return sqrt(e[0] * e[0] + e[1] * e[1] + e[2] * e[2]); }
    inline float squared_length() const { return e[0] * e[0] + e[1] * e[1] + e[2] * e[2]; }

    float e[3];
};

namespace {
    inline vec3 get_random_vec3()
    {
        return vec3(drand48(), drand48(), drand48());
    }

    inline vec3 get_vec3_one()
    {
        return vec3(1.0, 1.0, 1.0);
    }
}


inline vec3 operator+(const vec3 &v1, const vec3 &v2) {
    return vec3(v1.e[0] + v2.e[0], v1.e[1] + v2.e[1], v1.e[2] + v2.e[2]);
}

inline vec3 operator-(const vec3 &v1, const vec3 &v2) {
    return vec3(v1.e[0] - v2.e[0], v1.e[1] - v2.e[1], v1.e[2] - v2.e[2]);
}

inline vec3 operator*(const vec3 &v1, const vec3 &v2) {
    return vec3(v1.e[0] * v2.e[0], v1.e[1] * v2.e[1], v1.e[2] * v2.e[2]);
}

inline vec3 operator/(const vec3 &v1, const vec3 &v2) {
    return vec3(v1.e[0] / v2.e[0], v1.e[1] / v2.e[1], v1.e[2] / v2.e[2]);
}

inline vec3 operator/(const vec3 &v1, const float f) {
    return vec3(v1.e[0] / f, v1.e[1] / f, v1.e[2] / f);
}

inline vec3 operator+(const vec3 &v1, float f) {
    return vec3(v1.e[0] + f, v1.e[1] + f, v1.e[2] + f);
}

inline vec3 operator*(const float f, const vec3 &v1) {
    return vec3(v1.e[0] * f, v1.e[1] * f, v1.e[2] * f);
}

inline vec3 operator*(const vec3 &v1, const float f) {
    return vec3(v1.e[0] * f, v1.e[1] * f, v1.e[2] * f);
}

inline float dot(const vec3 &v1, const vec3 &v2) {
    return v1.e[0] * v2.e[0] + v1.e[1] * v2.e[1] + v1.e[2] * v2.e[2];
}

inline vec3 cross(const vec3 &v1, const vec3 &v2) {
    return vec3(
            v1.e[1] * v2.e[2] - v1.e[2] * v2.e[1],
           -(v1.e[0] * v2.e[2] - v1.e[2] * v2.e[0]),
           v1.e[0] * v2.e[1] - v1.e[1] * v2.e[0]
        );
}

inline vec3 unit_vector(vec3 v) {
    float len = v.length();
    return vec3(v.e[0] / len, v.e[1] / len, v.e[2] / len);
}

vec3 random_in_unit_sphere()
{
    vec3 p;
    do
    {
        p = 2.0 * get_random_vec3() - get_vec3_one();

    } while(dot(p,p) >= 1.0);

    return p;
}

vec3 reflect(const vec3& v, const vec3& n)
{
    return v - 2 * dot(v, n) * n;
}

bool refract(const vec3& v, const vec3& n, float ni_over_nt, vec3& refracted)
{
    vec3 uv = unit_vector(v);
    float dt = dot(uv, n);
    float discriminant = 1.0 - ni_over_nt * ni_over_nt * (1 - dt * dt);
    if (discriminant > 0)
    {
        refracted = ni_over_nt * (v - n * dt) - n * sqrt(discriminant);
        return true;
    }

    return false;
}

#endif