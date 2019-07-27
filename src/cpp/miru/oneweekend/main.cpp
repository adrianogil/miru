#include <iostream>
#include "sphere.h"
#include "hitablelist.h"
#include "float.h"


vec3 color(const ray& r, hitable *world)
{
    hit_record rec;

    if (world->hit(r, 0.0, MAXFLOAT, rec))
    {
        return 0.5 * (rec.normal + 1.0);
        // Show only a red color
        // return vec3(1, 0, 0);
    }
    vec3 unit_direction = unit_vector(r.direction());
    float t = 0.5 * (unit_direction.y() + 1.0);

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

    int obj_list_size = 1;
    hitable *list[obj_list_size];
    list[0] = new sphere(vec3(0, 0, -1), 0.5);
    // list[1] = new sphere(vec3(0, -100.5, -1), 100);

    hitable *world = new hitable_list(list, obj_list_size);

    for (int y = ny - 1; y >= 0; y--)
    {
        for (int x = 0; x < nx; x++)
        {
            float u = float(x) / float(nx);
            float v = float(y) / float(ny);

            ray r(origin, lower_left_corner + u * horizontal + v * vertical);
            vec3 col = color(r, world);

            int ir = int(255.99 * col[0]);
            int ig = int(255.99 * col[1]);
            int ib = int(255.99 * col[2]);

            std::cout << ir << " " << ig << " " << ib << "\n";
        }
    }

}