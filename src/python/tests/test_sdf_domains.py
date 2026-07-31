import math
import unittest

from miru.engine.vector import Vector3
from miru.raymarching.sdfdomains import (
    SDFBend,
    SDFElongation,
    SDFRepeat,
    SDFTwist,
)
from miru.raymarching.sdfsphere import SDFSphere


class SDFElongationTests(unittest.TestCase):
    def test_zero_elongation_is_identity(self):
        sphere = SDFSphere(1.0)
        elongated = SDFElongation(sphere, Vector3.zero())
        sample = Vector3(1.2, 0.3, -0.2)

        self.assertAlmostEqual(elongated.distance(sample), sphere.distance(sample))

    def test_sphere_elongates_along_x(self):
        elongated = SDFElongation(
            SDFSphere(1.0),
            Vector3(2.0, 0.0, 0.0),
        )

        self.assertAlmostEqual(
            elongated.distance(Vector3(3.0, 0.0, 0.0)),
            0.0,
        )
        self.assertAlmostEqual(
            elongated.distance(Vector3(0.0, 1.0, 0.0)),
            0.0,
        )

    def test_elongation_respects_center(self):
        center = Vector3(5.0, 0.0, 0.0)
        sphere = SDFSphere(1.0)
        sphere.transform.position = center
        elongated = SDFElongation(
            sphere,
            Vector3(1.0, 0.0, 0.0),
            center=center,
        )

        self.assertAlmostEqual(
            elongated.distance(Vector3(7.0, 0.0, 0.0)),
            0.0,
        )

    def test_elongation_rejects_negative_half_lengths(self):
        with self.assertRaises(ValueError):
            SDFElongation(SDFSphere(1.0), Vector3(-1.0, 0.0, 0.0))


class SDFRepeatTests(unittest.TestCase):
    def test_repeated_distance_is_periodic_on_enabled_axes(self):
        repeated = SDFRepeat(
            SDFSphere(0.4),
            period=Vector3(2.0, 1.0, 3.0),
            axes=("x", "z"),
        )
        sample = Vector3(0.2, 0.1, 0.3)

        self.assertAlmostEqual(
            repeated.distance(sample),
            repeated.distance(Vector3(2.2, 0.1, 3.3)),
        )

    def test_repeat_leaves_disabled_axis_unchanged(self):
        repeated = SDFRepeat(
            SDFSphere(0.4),
            period=Vector3(2.0, 1.0, 2.0),
            axes=("x", "z"),
        )

        self.assertNotAlmostEqual(
            repeated.distance(Vector3(0.0, 0.0, 0.0)),
            repeated.distance(Vector3(0.0, 1.0, 0.0)),
        )

    def test_repeat_validates_axes_and_periods(self):
        with self.assertRaises(ValueError):
            SDFRepeat(SDFSphere(1.0), Vector3.one(), axes=())
        with self.assertRaises(ValueError):
            SDFRepeat(SDFSphere(1.0), Vector3.one(), axes=("w",))
        with self.assertRaises(ValueError):
            SDFRepeat(
                SDFSphere(1.0),
                Vector3(0.0, 1.0, 1.0),
                axes=("x",),
            )


class SDFTwistTests(unittest.TestCase):
    def test_zero_twist_is_identity(self):
        sphere = SDFSphere(1.0)
        twisted = SDFTwist(sphere, strength=0.0)
        sample = Vector3(0.6, 0.8, 0.2)

        self.assertAlmostEqual(twisted.distance(sample), sphere.distance(sample))

    def test_twist_rotates_horizontal_slice(self):
        sphere = SDFSphere(0.2)
        sphere.transform.position = Vector3(1.0, 1.0, 0.0)
        twisted = SDFTwist(sphere, strength=math.pi * 0.5)

        self.assertAlmostEqual(
            twisted.distance(Vector3(0.0, 1.0, 1.0)),
            -0.2,
        )

    def test_twist_axis_is_unchanged(self):
        sphere = SDFSphere(1.0)
        twisted = SDFTwist(sphere, strength=2.0)
        sample = Vector3(0.0, 2.0, 0.0)

        self.assertAlmostEqual(twisted.distance(sample), sphere.distance(sample))


class SDFBendTests(unittest.TestCase):
    def test_zero_bend_is_identity(self):
        sphere = SDFSphere(1.0)
        bent = SDFBend(sphere, strength=0.0)
        sample = Vector3(0.7, -0.3, 0.2)

        self.assertAlmostEqual(bent.distance(sample), sphere.distance(sample))

    def test_bend_rotates_xy_sample_using_x_coordinate(self):
        sphere = SDFSphere(0.2)
        sphere.transform.position = Vector3(0.0, -1.0, 0.0)
        bent = SDFBend(sphere, strength=math.pi * 0.5)

        self.assertAlmostEqual(
            bent.distance(Vector3(1.0, 0.0, 0.0)),
            -0.2,
        )

    def test_bend_pivot_is_unchanged(self):
        sphere = SDFSphere(0.5)
        center = Vector3(1.0, 2.0, 0.0)
        sphere.transform.position = center
        bent = SDFBend(sphere, strength=1.0, center=center)

        self.assertAlmostEqual(bent.distance(center), -0.5)


if __name__ == "__main__":
    unittest.main()
