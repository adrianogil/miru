import unittest

from miru.engine.vector import Vector3
from miru.raymarching.sdfplane import SDFPlane
from miru.raymarching.sdfsphere import SDFSphere
from miru.raymarching.sdftorus import SDFTorus


class SDFSphereDistanceTests(unittest.TestCase):
    def setUp(self):
        self.sphere = SDFSphere(2.0)

    def test_center_distance_is_negative_radius(self):
        self.assertAlmostEqual(
            self.sphere.distance(Vector3.zero()),
            -2.0,
        )

    def test_surface_distance_is_zero(self):
        self.assertAlmostEqual(
            self.sphere.distance(Vector3(2.0, 0.0, 0.0)),
            0.0,
        )

    def test_distance_accounts_for_sphere_position(self):
        self.sphere.transform.position = Vector3(3.0, -1.0, 2.0)

        self.assertAlmostEqual(
            self.sphere.distance(Vector3(3.0, 1.0, 2.0)),
            0.0,
        )

    def test_radius_must_be_positive(self):
        with self.assertRaises(ValueError):
            SDFSphere(0.0)


class SDFPlaneDistanceTests(unittest.TestCase):
    def test_plane_has_positive_and_negative_half_spaces(self):
        plane = SDFPlane(Vector3.up(), offset=-1.0)

        self.assertAlmostEqual(plane.distance(Vector3(0.0, 1.0, 0.0)), 2.0)
        self.assertAlmostEqual(plane.distance(Vector3(0.0, -1.0, 0.0)), 0.0)
        self.assertAlmostEqual(plane.distance(Vector3(0.0, -2.0, 0.0)), -1.0)

    def test_normal_is_normalized(self):
        plane = SDFPlane(Vector3(0.0, 2.0, 0.0))

        self.assertAlmostEqual(plane.distance(Vector3(0.0, 3.0, 0.0)), 3.0)

    def test_distance_accounts_for_plane_position(self):
        plane = SDFPlane(Vector3.up())
        plane.transform.position = Vector3(0.0, 2.0, 0.0)

        self.assertAlmostEqual(plane.distance(Vector3(0.0, 2.0, 0.0)), 0.0)

    def test_normal_must_not_be_zero(self):
        with self.assertRaises(ValueError):
            SDFPlane(Vector3.zero())


class SDFTorusDistanceTests(unittest.TestCase):
    def setUp(self):
        self.torus = SDFTorus(2.0, 0.5)

    def test_outer_surface_distance_is_zero(self):
        self.assertAlmostEqual(
            self.torus.distance(Vector3(2.5, 0.0, 0.0)),
            0.0,
        )

    def test_tube_center_distance_is_negative_minor_radius(self):
        self.assertAlmostEqual(
            self.torus.distance(Vector3(2.0, 0.0, 0.0)),
            -0.5,
        )

    def test_center_hole_distance_is_positive(self):
        self.assertAlmostEqual(
            self.torus.distance(Vector3.zero()),
            1.5,
        )

    def test_distance_accounts_for_torus_position(self):
        self.torus.transform.position = Vector3(4.0, 1.0, -2.0)

        self.assertAlmostEqual(
            self.torus.distance(Vector3(6.5, 1.0, -2.0)),
            0.0,
        )

    def test_radii_must_be_positive(self):
        with self.assertRaises(ValueError):
            SDFTorus(0.0, 0.5)
        with self.assertRaises(ValueError):
            SDFTorus(2.0, 0.0)


if __name__ == "__main__":
    unittest.main()
