import sys

class Mesh:
    def __init__(self, vertices=[], triangles=[]):
        self.vertices = vertices
        self.triangles = triangles

    def add_triangle(self, t1, t2, t3):
        self.triangles.append(t1)
        self.triangles.append(t2)
        self.triangles.append(t3)

    def pre_render(self):
        pass

    # Checks if the specified ray hits the triagnlge descibed by p1, p2 and p3.
    # ray-triangle intersection algorithm implementation.
    # <param name="p1">Vertex 1 of the triangle.</param>
    # <param name="p2">Vertex 2 of the triangle.</param>
    # <param name="p3">Vertex 3 of the triangle.</param>
    # <param name="ray">The ray to test hit for.</param>
    # <returns><c>true</c> when the ray hits the triangle, otherwise <c>false</c></returns>
    def intercepts(self, ray):
        for t in xrange(0, len(self.triangles)/3):
            if self.intercept_triangle(t, ray):
                mean_vector = self.get_mean_triangle_vector(t)
                return (True, mean_vector)
        return (False, None)

    def get_mean_triangle_vector(self, t):
        p1 = self.vertices[self.triangles[3*t]]
        p2 = self.vertices[self.triangles[3*t+1]]
        p3 = self.vertices[self.triangles[3*t+2]]

        return p1.add(p2).add(p3).multiply(1.0/3.0)


    def intercept_triangle(self, t, ray):
        p1 = self.vertices[self.triangles[3*t]]
        p2 = self.vertices[self.triangles[3*t+1]]
        p3 = self.vertices[self.triangles[3*t+2]]

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
            return False;
        invDet = 1.0 / det

        # calculate distance from p1 to ray origin
        t = ray.origin.minus(p1);

        # Calculate u parameter
        u = t.dot_product(p) * invDet

        # Check for ray hit
        if u < 0 or u > 1:
            return False

        # Prepare to test v parameter
        q = t.cross_product(e1)

        # Calculate v parameter
        v = ray.direction.dot_product(q) * invDet

        # Check for ray hit
        if v < 0 or u + v > 1: 
            return False

        if (e2.dot_product(q) * invDet) > epsilon:
            # ray does intersect
            return True

        # No hit at all
        return False
