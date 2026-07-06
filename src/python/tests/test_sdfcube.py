import math
import unittest

from miru.engine.vector import Vector3
from miru.raymarching.sdfcube import SDFCube


class SDFCubeDistanceTests(unittest.TestCase):
    def setUp(self):
        self.cube = SDFCube(Vector3(2.0, 4.0, 6.0))

    def test_inside_distance_is_negative(self):
        self.assertAlmostEqual(self.cube.distance(Vector3(0.0, 0.0, 0.0)), -1.0)

    def test_surface_distance_is_zero(self):
        self.assertAlmostEqual(self.cube.distance(Vector3(1.0, 0.0, 0.0)), 0.0)

    def test_axis_exterior_distance_uses_nearest_surface(self):
        self.assertAlmostEqual(self.cube.distance(Vector3(1.5, 0.0, 0.0)), 0.5)

    def test_corner_exterior_distance_is_euclidean(self):
        self.assertAlmostEqual(
            self.cube.distance(Vector3(2.0, 3.0, 4.0)),
            math.sqrt(3.0),
        )

    def test_distance_accounts_for_cube_position(self):
        self.cube.transform.position = Vector3(10.0, -2.0, 5.0)

        self.assertAlmostEqual(
            self.cube.distance(Vector3(11.0, -2.0, 5.0)),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
