import sys

from vector import Vector3, Vector2

import numpy as np

import meshtools

class Mesh:
    def __init__(self, vertices=[], triangles=[]):
        self.vertices = vertices
        self.triangles = triangles
        self.uvs = None
        self.normals = None
        self.material = None

    def add_triangle(self, t1, t2, t3):
        self.triangles.append(t1)
        self.triangles.append(t2)
        self.triangles.append(t3)

    def pre_render(self):
        pass

    def render(self, scene, interception):
        if self.material != None:
            return self.material.render(scene, interception)

    # Checks if the specified ray hits the triagnlge descibed by p1, p2 and p3.
    # ray-triangle intersection algorithm implementation.
    # <param name="p1">Vertex 1 of the triangle.</param>
    # <param name="p2">Vertex 2 of the triangle.</param>
    # <param name="p3">Vertex 3 of the triangle.</param>
    # <param name="ray">The ray to test hit for.</param>
    # <returns><c>true</c> when the ray hits the triangle, otherwise <c>false</c></returns>
    def intercepts(self, ray):
        for t in xrange(0, len(self.triangles)/3):
            intersection_data  = self.intercept_triangle(t, ray)
            if intersection_data['result']:
                return intersection_data
        return {'result': False, 'hit_point': Vector3.zero, 'normal' : None, 'uv' : Vector2.zero} 

    def get_mean_triangle_vector(self, t):
        p1 = self.vertices[self.triangles[3*t]]
        p2 = self.vertices[self.triangles[3*t+1]]
        p3 = self.vertices[self.triangles[3*t+2]]

        return p1.add(p2).add(p3).multiply(1.0/3.0)


    def intercept_triangle(self, t, ray):

        result = {'result': False, 'hit_point': Vector3.zero, 'normal' : None, 'uv' : Vector2.zero}

        t1 = self.triangles[3*t]
        t2 = self.triangles[3*t+1]
        t3 = self.triangles[3*t+2]

        p1 = self.vertices[t1]
        p2 = self.vertices[t2]
        p3 = self.vertices[t3]

        # Vectors from p1 to p2/p3 (edges)
        # Find vectors for two edges sharing vertex/point p1
        e1 = p2.minus(p1)
        e2 = p3.minus(p1)

        # calculating determinant 
        p = ray.direction.cross_product(e2)

        # Calculate determinat
        det = e1.dot_product(p)

        epsilon = sys.float_info.epsilon

        # if determinant is near zero, ray lies in plane of triangle otherwise not
        if det > -epsilon and det < epsilon:
            return result;
        invDet = 1.0 / det

        # calculate distance from p1 to ray origin
        t = ray.origin.minus(p1);

        # Calculate u parameter
        u = t.dot_product(p) * invDet

        # Check for ray hit
        if u < 0 or u > 1:
            return result

        # Prepare to test v parameter
        q = t.cross_product(e1)

        # Calculate v parameter
        v = ray.direction.dot_product(q) * invDet

        # Check for ray hit
        if v < 0 or u + v > 1: 
            return result

        if (e2.dot_product(q) * invDet) > epsilon:

            n = e1.normalized().cross_product(e2.normalized()).normalized()
            denom = n.dot_product(ray.direction)

            # print(str(denom))
            if np.abs(denom) > 1e-6:
                if denom < 0:
                    return result
                    # n.multiply(-1, False)

            
            p1l0 = p1.minus(ray.origin)
            t = p1l0.dot_product(n)

            if t < 0:
                return result

            hit_point = ray.origin.add(ray.direction.multiply(t))
            bary_coord = meshtools.barycentric(hit_point, p1, p2, p3)

            if self.uvs != None:
                uv = self.uvs[t1].multiply(bary_coord.x)
                uv = uv.add(self.uvs[t2].multiply(bary_coord.y))
                uv = uv.add(self.uvs[t3].multiply(bary_coord.z))
            else:
                uv = None

            # print('mesh.intercepts - hit_point - ' + str(hit_point))
            # print('mesh.intercepts - normal - ' + str(n))
            # print('mesh.intercepts - uv - ' + str(uv))

            # ray does intersect
            result['result'] = True
            result['hit_point'] = hit_point
            result['normal'] = n.multiply(-1)
            result['uv'] = uv

            return result

        # No hit at all
        return result
