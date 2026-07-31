import unittest

from miru.engine.vector import Vector3
from miru.raymarching import (
    SDFElongation,
    SDFIntersection,
    SDFRepeat,
    SDFRound,
    SDFShell,
    SDFSmoothSubtraction,
    SDFSphere,
    SDFTwist,
)
from miru.raymarching.sdfcube import SDFCube


class SDFCompositionTests(unittest.TestCase):
    def test_binary_modifier_and_domain_operations_compose(self):
        clipped_sphere = SDFIntersection(
            SDFSphere(1.2),
            SDFCube(Vector3(2.0, 1.5, 2.0)),
        )
        model = SDFRepeat(
            SDFTwist(
                SDFShell(clipped_sphere, thickness=0.08),
                strength=0.35,
            ),
            period=Vector3(3.0, 1.0, 3.0),
            axes=("x", "z"),
        )

        self.assertIsInstance(model.distance(Vector3(0.2, 0.3, 0.4)), float)
        self.assertAlmostEqual(
            model.distance(Vector3(0.2, 0.3, 0.4)),
            model.distance(Vector3(3.2, 0.3, 3.4)),
        )

    def test_round_elongation_and_smooth_subtraction_compose(self):
        capsule = SDFRound(
            SDFElongation(
                SDFSphere(0.5),
                half_length=Vector3(0.8, 0.0, 0.0),
            ),
            radius=0.1,
        )
        model = SDFSmoothSubtraction(
            capsule,
            SDFSphere(0.3),
            smoothing=0.12,
        )

        self.assertGreater(model.distance(Vector3.zero()), 0.0)
        self.assertLess(model.distance(Vector3(0.8, 0.0, 0.0)), 0.0)


if __name__ == "__main__":
    unittest.main()
