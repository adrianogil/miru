import unittest

from miru.engine.vector import Vector3
from miru.raymarching.sdfoperations import (
    SDFIntersection,
    SDFSmoothIntersection,
    SDFSmoothSubtraction,
    SDFSmoothUnion,
    SDFSubtraction,
    SDFUnion,
    smooth_max,
    smooth_min,
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


class SDFIntersectionTests(unittest.TestCase):
    def test_intersection_returns_farthest_operand_distance(self):
        left = SDFSphere(2.0)
        right = SDFSphere(1.0)
        right.transform.position = Vector3(1.0, 0.0, 0.0)
        intersection = SDFIntersection(left, right)

        self.assertAlmostEqual(intersection.distance(Vector3.zero()), 0.0)
        self.assertAlmostEqual(
            intersection.distance(Vector3(1.0, 0.0, 0.0)),
            -1.0,
        )

    def test_intersection_is_symmetric(self):
        left = SDFSphere(1.4)
        right = SDFSphere(1.0)
        right.transform.position = Vector3(0.5, 0.0, 0.0)
        sample = Vector3(0.2, 0.4, -0.1)

        self.assertAlmostEqual(
            SDFIntersection(left, right).distance(sample),
            SDFIntersection(right, left).distance(sample),
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


class SDFSmoothBooleanTests(unittest.TestCase):
    def setUp(self):
        self.left = SDFSphere(1.25)
        self.left.transform.position = Vector3(-0.35, 0.0, 0.0)
        self.right = SDFSphere(1.0)
        self.right.transform.position = Vector3(0.45, 0.0, 0.0)

    def test_scalar_smooth_min_and_max_are_duals(self):
        self.assertAlmostEqual(
            smooth_max(0.2, -0.6, 0.4),
            -smooth_min(-0.2, 0.6, 0.4),
        )

    def test_smooth_intersection_is_symmetric(self):
        sample = Vector3(0.1, 0.35, 0.2)
        left_right = SDFSmoothIntersection(
            self.left,
            self.right,
            smoothing=0.3,
        )
        right_left = SDFSmoothIntersection(
            self.right,
            self.left,
            smoothing=0.3,
        )

        self.assertAlmostEqual(
            left_right.distance(sample),
            right_left.distance(sample),
        )

    def test_smooth_intersection_matches_hard_operation_outside_blend(self):
        sample = Vector3(-2.0, 0.0, 0.0)

        self.assertAlmostEqual(
            SDFSmoothIntersection(
                self.left,
                self.right,
                smoothing=0.2,
            ).distance(sample),
            SDFIntersection(self.left, self.right).distance(sample),
        )

    def test_smooth_subtraction_rounds_cut_boundary(self):
        outer = SDFSphere(2.0)
        cutter = SDFSphere(1.0)
        sample = Vector3(1.5, 0.0, 0.0)

        hard = SDFSubtraction(outer, cutter).distance(sample)
        smooth = SDFSmoothSubtraction(
            outer,
            cutter,
            smoothing=1.0,
        ).distance(sample)

        self.assertGreater(smooth, hard)

    def test_smooth_operations_require_positive_smoothing(self):
        with self.assertRaises(ValueError):
            SDFSmoothIntersection(self.left, self.right, smoothing=0.0)
        with self.assertRaises(ValueError):
            SDFSmoothSubtraction(self.left, self.right, smoothing=-0.1)
        with self.assertRaises(ValueError):
            smooth_min(0.0, 0.0, 0.0)


class SDFOperationValidationTests(unittest.TestCase):
    def test_operations_require_two_operands(self):
        with self.assertRaises(ValueError):
            SDFUnion(SDFSphere(1.0), None)


if __name__ == "__main__":
    unittest.main()
