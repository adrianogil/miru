from vector import Vector3

# Compute barycentric coordinates (u, v, w) for
# point p with respect to triangle (a, b, c)
# Based on https://gamedev.stackexchange.com/questions/23743/whats-the-most-efficient-way-to-find-barycentric-coordinates
def barycentric(p, a, b, c):
    v0 = b.minus(a)
    v1 = c.minus(a)
    v2 = p.minus(a)
    d00 = v0.dot_product(v0);
    d01 = v0.dot_product(v1);
    d11 = v1.dot_product(v1);
    d20 = v2.dot_product(v0);
    d21 = v2.dot_product(v1);
    denom = d00 * d11 - d01 * d01;
    v = (d11 * d20 - d01 * d21) / denom;
    w = (d00 * d21 - d01 * d20) / denom;
    u = 1.0 - v - w;

    return Vector3(u,v,w)