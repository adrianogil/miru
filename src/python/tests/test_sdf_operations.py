import unittest

from miru.engine.vector import Vector3
from miru.raymarching.sdfoperations import (
    SDFSmoothUnion,
    SDFSubtraction,
    SDFUnion,
)
from miru.raymarching.sdfsphere import SDFSphere


class SDFUnionTests(unittest.TestCase):
    def test_union_returns_nearest_operand_distance(self):
        left = SDFSphere(1.0)
        left.transform.position = Vector3(-1.0, 0.0, 0.0)
        right = SDFSphere(1.0)
        right.transform.position = Vector3(1.0, 0.0, 0.0)
        union = SDFUnion(left, right)

        self.assertAlmostEqual(union.distance(Vector3(-1.0, 0.0, 0.0)), -1.0)
        self.assertAlmostEqual(union.distance(Vector3.zero()), 0.0)


class SDFSubtractionTests(unittest.TestCase):
    def test_subtraction_removes_right_operand_from_left(self):
        outer = SDFSphere(2.0)
        cutter = SDFSphere(1.0)
        subtraction = SDFSubtraction(outer, cutter)

        self.assertAlmostEqual(subtraction.distance(Vector3.zero()), 1.0)
        self.assertAlmostEqual(
            subtraction.distance(Vector3(1.5, 0.0, 0.0)),
            -0.5,
        )
        self.assertAlmostEqual(
            subtraction.distance(Vector3(2.0, 0.0, 0.0)),
            0.0,
        )


class SDFSmoothUnionTests(unittest.TestCase):
    def test_smooth_union_blends_equal_distances(self):
        left = SDFSphere(1.0)
        left.transform.position = Vector3(-0.75, 0.0, 0.0)
        right = SDFSphere(1.0)
        right.transform.position = Vector3(0.75, 0.0, 0.0)
        union = SDFSmoothUnion(left, right, smoothing=1.0)

        self.assertAlmostEqual(union.distance(Vector3.zero()), -0.5)

    def test_smooth_union_is_symmetric(self):
        left = SDFSphere(1.0)
        left.transform.position = Vector3(-0.75, 0.0, 0.0)
        right = SDFSphere(1.0)
        right.transform.position = Vector3(0.75, 0.0, 0.0)

        left_right = SDFSmoothUnion(left, right, smoothing=0.4)
        right_left = SDFSmoothUnion(right, left, smoothing=0.4)
        sample = Vector3(0.2, 0.3, 0.1)

        self.assertAlmostEqual(
            left_right.distance(sample),
            right_left.distance(sample),
        )

    def test_smoothing_must_be_positive(self):
        left = SDFSphere(1.0)
        right = SDFSphere(1.0)

        with self.assertRaises(ValueError):
            SDFSmoothUnion(left, right, smoothing=0.0)


class SDFOperationValidationTests(unittest.TestCase):
    def test_operations_require_two_operands(self):
        with self.assertRaises(ValueError):
            SDFUnion(SDFSphere(1.0), None)


if __name__ == "__main__":
    unittest.main()
