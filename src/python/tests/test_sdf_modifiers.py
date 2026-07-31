import unittest

from miru.engine.vector import Vector3
from miru.raymarching.sdfmodifiers import SDFRound, SDFShell
from miru.raymarching.sdfsphere import SDFSphere


class SDFShellTests(unittest.TestCase):
    def setUp(self):
        self.shell = SDFShell(SDFSphere(1.0), thickness=0.1)

    def test_original_surface_is_inside_shell(self):
        self.assertAlmostEqual(
            self.shell.distance(Vector3(1.0, 0.0, 0.0)),
            -0.1,
        )

    def test_shell_has_inner_and_outer_surfaces(self):
        self.assertAlmostEqual(
            self.shell.distance(Vector3(0.9, 0.0, 0.0)),
            0.0,
        )
        self.assertAlmostEqual(
            self.shell.distance(Vector3(1.1, 0.0, 0.0)),
            0.0,
        )

    def test_shell_thickness_must_be_positive(self):
        with self.assertRaises(ValueError):
            SDFShell(SDFSphere(1.0), thickness=0.0)


class SDFRoundTests(unittest.TestCase):
    def test_rounding_subtracts_radius_from_child_distance(self):
        sphere = SDFSphere(1.0)
        rounded = SDFRound(sphere, radius=0.25)
        sample = Vector3(2.0, 0.0, 0.0)

        self.assertAlmostEqual(
            rounded.distance(sample),
            sphere.distance(sample) - 0.25,
        )

    def test_zero_radius_is_identity(self):
        sphere = SDFSphere(1.0)
        rounded = SDFRound(sphere, radius=0.0)
        sample = Vector3(0.3, 0.4, 0.5)

        self.assertAlmostEqual(rounded.distance(sample), sphere.distance(sample))

    def test_rounding_radius_must_not_be_negative(self):
        with self.assertRaises(ValueError):
            SDFRound(SDFSphere(1.0), radius=-0.1)


class SDFUnaryValidationTests(unittest.TestCase):
    def test_unary_operations_require_a_child(self):
        with self.assertRaises(ValueError):
            SDFRound(None, radius=0.1)


if __name__ == "__main__":
    unittest.main()
