#include <iostream>
#include "ray.h"

float hit_sphere(const vec3& center, float radius, const ray& r)
{
    vec3 oc = r.origin() - center;
    float a = dot(r.direction(), r.direction());
    float b = 2.0 * dot(oc, r.direction());
    float c = dot(oc, oc) - radius * radius;
    float discriminant = b * b - 4 * a * c;

    if (discriminant < 0)
    {
        return -1.0;
    } else {
        return (-b - sqrt(discriminant)) / (2.0 * a);
    }
}

vec3 color(const ray& r)
{
    float t = hit_sphere(vec3(0,0,-1), 0.5, r);
    // return vec3(t, 0, 0);
    if (t > 0.0)
    {
        vec3 N = unit_vector(r.point_at(t) - vec3(0, 0, -1));
        return 0.5 * (N + 1.0);
    }
    vec3 unit_direction = unit_vector(r.direction());
    t = 0.5 * (unit_direction.y() + 1.0);

    return (1.0 - t) * vec3(1.0, 1.0, 1.0) + t * vec3(0.5, 0.7, 1.0);
}

int main()
{

    int nx = 200;
    int ny = 100;

    std::cout << "P3\n" << nx << " " << ny << "\n255\n";

    vec3 lower_left_corner(-2.0, -1.0, -1.0);
    vec3 horizontal(4.0, 0.0, 0.0);
    vec3 vertical(0.0, 2.0, 0.0);
    vec3 origin(0.0, 0.0, 0.0);

    for (int y = ny - 1; y >= 0; y--)
    {
        for (int x = 0; x < nx; x++)
        {
            float u = float(x) / float(nx);
            float v = float(y) / float(ny);

            ray r(origin, lower_left_corner + u * horizontal + v * vertical);
            vec3 col = color(r);

            int ir = int(255.99 * col[0]);
            int ig = int(255.99 * col[1]);
            int ib = int(255.99 * col[2]);

            std::cout << ir << " " << ig << " " << ib << "\n";
        }
    }

}