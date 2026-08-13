import math
import unittest

from miru.engine.camera import Camera
from miru.engine.vector import Vector3
from miru.raytracing.bvh import AABB, BVH, brute_force_closest_hit
from miru.raytracing.cube import Cube
from miru.raytracing.plane import Plane
from miru.raytracing.ray import Ray
from miru.raytracing.scene import Scene
from miru.raytracing.sphere import Sphere


def ray(origin, target):
    return Ray(Vector3(*origin), Vector3(*target))


def prepared_sphere(position, radius=1.0, sphere_type=Sphere):
    sphere = sphere_type(radius)
    sphere.transform.position = Vector3(*position)
    sphere.pre_render()
    return sphere


class AABBTests(unittest.TestCase):
    def setUp(self):
        self.box = AABB(Vector3(-1, -1, 4), Vector3(1, 1, 6))

    def test_hit_miss_and_interval_clipping(self):
        center_ray = ray((0, 0, 0), (0, 0, 1))

        self.assertEqual(self.box.intersection_interval(center_ray), (4.0, 6.0))
        self.assertTrue(self.box.intersects(center_ray, t_max=4.0))
        self.assertFalse(self.box.intersects(center_ray, t_max=3.99))
        self.assertFalse(self.box.intersects(ray((3, 0, 0), (3, 0, 1))))

    def test_parallel_rays_handle_inside_and_outside_slabs(self):
        self.assertTrue(self.box.intersects(ray((0, 0, 5), (0, 1, 5))))
        self.assertFalse(self.box.intersects(ray((2, 0, 5), (2, 1, 5))))

    def test_origin_inside_tangent_and_box_behind_ray(self):
        self.assertEqual(
            self.box.intersection_interval(ray((0, 0, 5), (0, 0, 6))),
            (0.0, 1.0),
        )
        self.assertTrue(self.box.intersects(ray((1, 2, 5), (1, 0, 5))))
        behind = AABB(Vector3(-1, -1, -6), Vector3(1, 1, -4))
        self.assertFalse(behind.intersects(ray((0, 0, 0), (0, 0, 1))))

    def test_degenerate_flat_box_can_be_hit(self):
        flat = AABB(Vector3(-1, -1, 5), Vector3(1, 1, 5))

        self.assertTrue(flat.intersects(ray((0, 0, 0), (0, 0, 1))))

    def test_union_and_invalid_bounds(self):
        other = AABB(Vector3(2, -2, 3), Vector3(4, 0, 8))
        union = self.box.union(other)

        self.assertEqual(union.minimum.x, -1.0)
        self.assertEqual(union.minimum.y, -2.0)
        self.assertEqual(union.maximum.x, 4.0)
        self.assertEqual(union.maximum.z, 8.0)
        with self.assertRaises(ValueError):
            AABB(Vector3(1, 0, 0), Vector3(0, 1, 1))
        with self.assertRaises(ValueError):
            AABB.from_points([])


class BVHConstructionTests(unittest.TestCase):
    def test_empty_singleton_and_leaf_size_validation(self):
        self.assertIsNone(BVH([]).root)
        sphere = prepared_sphere((0, 0, 5))
        singleton = BVH([sphere], leaf_size=1)
        self.assertTrue(singleton.root.is_leaf)
        self.assertEqual(singleton.root.primitives[0].obj, sphere)
        with self.assertRaises(ValueError):
            BVH([sphere], leaf_size=0)

    def test_build_terminates_for_identical_centroids_and_respects_leaf_size(self):
        spheres = [prepared_sphere((0, 0, 5), radius=1 + i * 0.05) for i in range(9)]
        bvh = BVH(spheres, leaf_size=2)

        stack = [bvh.root]
        leaf_count = 0
        while stack:
            node = stack.pop()
            if node.is_leaf:
                leaf_count += 1
                self.assertLessEqual(len(node.primitives), 2)
            else:
                self.assertIsNotNone(node.left)
                self.assertIsNotNone(node.right)
                stack.extend((node.left, node.right))
        self.assertGreater(leaf_count, 1)

    def test_parent_bounds_contain_every_primitive(self):
        spheres = [
            prepared_sphere((-3, 1, 6), 0.5),
            prepared_sphere((2, -2, 12), 2.0),
            prepared_sphere((5, 3, 8), 1.0),
        ]
        bounds = BVH(spheres, leaf_size=1).root.bounds

        self.assertEqual(bounds.minimum.x, -3.5)
        self.assertEqual(bounds.minimum.y, -4.0)
        self.assertEqual(bounds.maximum.x, 6.0)
        self.assertEqual(bounds.maximum.z, 14.0)


class BVHCorrectnessTests(unittest.TestCase):
    def setUp(self):
        self.objects = [
            prepared_sphere((-3, 0, 8), 1.0),
            prepared_sphere((0, 0, 10), 2.0),
            prepared_sphere((0, 0, 5), 0.75),
            prepared_sphere((3, 1, 9), 1.5),
            prepared_sphere((0, -3, 12), 1.0),
        ]
        self.bvh = BVH(self.objects, leaf_size=2)

    def assert_matches_brute_force(self, target_ray, max_distance=math.inf):
        brute = brute_force_closest_hit(
            target_ray,
            self.objects,
            max_distance=max_distance,
        )
        accelerated = self.bvh.closest_hit(target_ray, max_distance=max_distance)
        if brute is None:
            self.assertIsNone(accelerated)
        else:
            self.assertIs(brute[0], accelerated[0])
            self.assertEqual(brute[3], accelerated[3])
            self.assertAlmostEqual(brute[2], accelerated[2])

    def test_matches_brute_force_for_hits_misses_and_tangents(self):
        rays = [
            ray((0, 0, 0), (0, 0, 1)),
            ray((0, 0, 0), (-3, 0, 8)),
            ray((0, 0, 0), (3, 1, 9)),
            ray((0, 0, 0), (20, 20, 1)),
            ray((0.75, 0, 0), (0.75, 0, 5)),
            ray((0, 0, 5), (0, 0, 6)),
        ]
        for target_ray in rays:
            with self.subTest(ray=str(target_ray)):
                self.assert_matches_brute_force(target_ray)

    def test_max_distance_clips_hits(self):
        target_ray = ray((0, 0, 0), (0, 0, 1))

        self.assert_matches_brute_force(target_ray, max_distance=4.0)
        self.assertIsNone(self.bvh.closest_hit(target_ray, max_distance=4.24))
        self.assertIsNotNone(self.bvh.closest_hit(target_ray, max_distance=4.25))

    def test_equal_distance_tie_preserves_scene_insertion_order(self):
        first = prepared_sphere((0, 0, 5), 1.0)
        second = prepared_sphere((0, 0, 5), 1.0)

        hit = BVH([first, second], leaf_size=1).closest_hit(
            ray((0, 0, 0), (0, 0, 1))
        )

        self.assertIs(hit[0], first)
        self.assertEqual(hit[3], 0)

    def test_cube_and_finite_plane_match_brute_force_for_oblique_ray(self):
        cube = Cube()
        cube.transform.position = Vector3(0, 0, 5)
        cube.pre_render()
        plane = Plane(
            [
                Vector3(-1, -1, 8),
                Vector3(1, -1, 8),
                Vector3(1, 1, 8),
                Vector3(-1, 1, 8),
            ]
        )
        plane.pre_render()
        objects = [plane, cube]
        target_ray = ray((2, 0, 0), (0, 0, 5))

        brute = brute_force_closest_hit(target_ray, objects)
        accelerated = BVH(objects, leaf_size=1).closest_hit(target_ray)

        self.assertIs(brute[0], cube)
        self.assertIs(accelerated[0], brute[0])
        self.assertAlmostEqual(accelerated[2], brute[2])
        self.assertIsNotNone(accelerated[1]["normal"])

    def test_object_without_bounds_uses_brute_force_fallback(self):
        class UnboundedHit:
            def intercepts(self, target_ray):
                return {
                    "result": True,
                    "hit_point": target_ray.origin.add(
                        target_ray.direction.multiply(2.0)
                    ),
                    "normal": Vector3.forward().multiply(-1),
                    "uv": None,
                }

        far_sphere = prepared_sphere((0, 0, 8), 1.0)
        fallback = UnboundedHit()

        hit = BVH([far_sphere, fallback]).closest_hit(
            ray((0, 0, 0), (0, 0, 1))
        )

        self.assertIs(hit[0], fallback)
        self.assertEqual(hit[3], 1)


class BVHSceneIntegrationTests(unittest.TestCase):
    def test_scene_accelerated_and_reference_paths_agree(self):
        scene = Scene()
        camera = Camera()
        camera.far = 100
        scene.set_camera(camera)
        for position in ((0, 0, 8), (0, 0, 4), (3, 0, 6)):
            scene.add_objects(prepared_sphere(position, 0.5))
        target_ray = ray((0, 0, 0), (0, 0, 1))

        accelerated = scene.closest_hit(target_ray, accelerated=True)
        reference = scene.closest_hit(target_ray, accelerated=False)

        self.assertIs(accelerated[0], reference[0])
        self.assertAlmostEqual(accelerated[2], reference[2])

    def test_adding_an_object_invalidates_the_bvh(self):
        scene = Scene()
        camera = Camera()
        camera.far = 100
        scene.set_camera(camera)
        far = prepared_sphere((0, 0, 10), 1.0)
        scene.add_objects(far)
        target_ray = ray((0, 0, 0), (0, 0, 1))
        self.assertIs(scene.closest_hit(target_ray)[0], far)

        near = prepared_sphere((0, 0, 4), 1.0)
        scene.add_objects(near)

        self.assertIsNone(scene._bvh)
        self.assertIs(scene.closest_hit(target_ray)[0], near)

    def test_prepare_rebuilds_after_transform_changes(self):
        scene = Scene()
        camera = Camera()
        camera.far = 100
        scene.set_camera(camera)
        sphere = prepared_sphere((0, 0, 5), 1.0)
        scene.add_objects(sphere)
        target_ray = ray((0, 0, 0), (0, 0, 1))
        self.assertIsNotNone(scene.closest_hit(target_ray))

        sphere.transform.position = Vector3(20, 0, 5)
        scene.prepare()

        self.assertIsNone(scene.closest_hit(target_ray))

    def test_bvh_reduces_shape_intersection_calls_in_large_scene(self):
        class CountingSphere(Sphere):
            calls = 0

            def intercepts(self, target_ray):
                type(self).calls += 1
                return super().intercepts(target_ray)

        objects = [
            prepared_sphere((index * 3.0, 0, 8), 0.75, CountingSphere)
            for index in range(64)
        ]
        target_ray = ray((0, 0, 0), (0, 0, 1))

        CountingSphere.calls = 0
        brute = brute_force_closest_hit(target_ray, objects)
        brute_calls = CountingSphere.calls
        CountingSphere.calls = 0
        accelerated = BVH(objects, leaf_size=2).closest_hit(target_ray)
        bvh_calls = CountingSphere.calls

        self.assertIs(accelerated[0], brute[0])
        self.assertEqual(brute_calls, 64)
        self.assertLessEqual(bvh_calls, 4)


if __name__ == "__main__":
    unittest.main()
