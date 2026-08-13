"""Bounding-volume hierarchy acceleration for Miru's CPU ray tracer."""

from dataclasses import dataclass
import math

from miru.engine.vector import Vector3


@dataclass(frozen=True)
class AABB:
    minimum: Vector3
    maximum: Vector3

    def __post_init__(self):
        if (
            self.minimum.x > self.maximum.x
            or self.minimum.y > self.maximum.y
            or self.minimum.z > self.maximum.z
        ):
            raise ValueError("AABB minimum must not exceed maximum")

    @classmethod
    def from_points(cls, points):
        points = list(points)
        if not points:
            raise ValueError("Cannot construct an AABB without points")
        return cls(
            Vector3(
                min(point.x for point in points),
                min(point.y for point in points),
                min(point.z for point in points),
            ),
            Vector3(
                max(point.x for point in points),
                max(point.y for point in points),
                max(point.z for point in points),
            ),
        )

    @classmethod
    def union_all(cls, boxes):
        boxes = list(boxes)
        if not boxes:
            raise ValueError("Cannot union an empty collection of AABBs")
        return cls.from_points(
            [box.minimum for box in boxes] + [box.maximum for box in boxes]
        )

    def union(self, other):
        return AABB.from_points(
            [self.minimum, self.maximum, other.minimum, other.maximum]
        )

    def centroid(self):
        return self.minimum.add(self.maximum).multiply(0.5)

    def extent(self):
        return self.maximum.minus(self.minimum)

    def longest_axis(self):
        extent = self.extent()
        if extent.x >= extent.y and extent.x >= extent.z:
            return 0
        if extent.y >= extent.z:
            return 1
        return 2

    def intersection_interval(self, ray, t_min=0.0, t_max=math.inf):
        """Return the inclusive ray interval through this box, or None."""
        entry = t_min
        exit_distance = t_max
        for axis in ("x", "y", "z"):
            origin = getattr(ray.origin, axis)
            direction = getattr(ray.direction, axis)
            slab_min = getattr(self.minimum, axis)
            slab_max = getattr(self.maximum, axis)

            if abs(direction) <= 1e-15:
                if origin < slab_min or origin > slab_max:
                    return None
                continue

            inverse_direction = 1.0 / direction
            near = (slab_min - origin) * inverse_direction
            far = (slab_max - origin) * inverse_direction
            if near > far:
                near, far = far, near
            entry = max(entry, near)
            exit_distance = min(exit_distance, far)
            if exit_distance < entry:
                return None
        return (entry, exit_distance)

    def intersects(self, ray, t_min=0.0, t_max=math.inf):
        return self.intersection_interval(ray, t_min=t_min, t_max=t_max) is not None


@dataclass(frozen=True)
class BVHPrimitive:
    obj: object
    bounds: AABB
    index: int


class BVHNode:
    def __init__(self, bounds, left=None, right=None, primitives=None):
        self.bounds = bounds
        self.left = left
        self.right = right
        self.primitives = tuple(primitives or ())

    @property
    def is_leaf(self):
        return self.left is None and self.right is None


def _coordinate(vector, axis):
    return (vector.x, vector.y, vector.z)[axis]


def _build_node(primitives, leaf_size):
    bounds = AABB.union_all(primitive.bounds for primitive in primitives)
    if len(primitives) <= leaf_size:
        return BVHNode(
            bounds,
            primitives=sorted(primitives, key=lambda primitive: primitive.index),
        )

    centroid_bounds = AABB.from_points(
        primitive.bounds.centroid() for primitive in primitives
    )
    axis = centroid_bounds.longest_axis()
    ordered = sorted(
        primitives,
        key=lambda primitive: (
            _coordinate(primitive.bounds.centroid(), axis),
            primitive.index,
        ),
    )
    midpoint = len(ordered) // 2
    return BVHNode(
        bounds,
        left=_build_node(ordered[:midpoint], leaf_size),
        right=_build_node(ordered[midpoint:], leaf_size),
    )


def _hit_distance(ray, intersection):
    return intersection["hit_point"].minus(ray.origin).magnitude()


def _candidate_is_closer(distance, index, best_distance, best_index):
    return distance < best_distance or (
        distance == best_distance and index < best_index
    )


def brute_force_closest_hit(ray, objects, max_distance=math.inf):
    """Return the closest `(object, intersection, distance, index)` tuple."""
    best = None
    best_distance = max_distance
    best_index = math.inf
    for index, obj in enumerate(objects):
        intersection = obj.intercepts(ray)
        if not intersection["result"]:
            continue
        distance = _hit_distance(ray, intersection)
        if distance <= max_distance and _candidate_is_closer(
            distance, index, best_distance, best_index
        ):
            best = (obj, intersection, distance, index)
            best_distance = distance
            best_index = index
    return best


class BVH:
    """A deterministic median-split BVH plus unbounded-object fallback."""

    def __init__(self, objects, leaf_size=4):
        if not isinstance(leaf_size, int) or leaf_size < 1:
            raise ValueError("BVH leaf_size must be a positive integer")
        self.objects = tuple(objects)
        self.leaf_size = leaf_size
        bounded = []
        self.unbounded = []
        for index, obj in enumerate(self.objects):
            bounding_box = getattr(obj, "bounding_box", None)
            bounds = bounding_box() if callable(bounding_box) else None
            if bounds is None:
                self.unbounded.append((index, obj))
            elif not isinstance(bounds, AABB):
                raise TypeError("bounding_box() must return an AABB or None")
            else:
                bounded.append(BVHPrimitive(obj, bounds, index))
        self.root = _build_node(bounded, leaf_size) if bounded else None

    def _visit_node(self, node, ray, best, max_distance):
        if node is None:
            return best
        best_distance = max_distance if best is None else best[2]
        if not node.bounds.intersects(ray, t_max=best_distance):
            return best

        if node.is_leaf:
            for primitive in node.primitives:
                intersection = primitive.obj.intercepts(ray)
                if not intersection["result"]:
                    continue
                distance = _hit_distance(ray, intersection)
                best_distance = max_distance if best is None else best[2]
                best_index = math.inf if best is None else best[3]
                if distance <= max_distance and _candidate_is_closer(
                    distance, primitive.index, best_distance, best_index
                ):
                    best = (
                        primitive.obj,
                        intersection,
                        distance,
                        primitive.index,
                    )
            return best

        best_distance = max_distance if best is None else best[2]
        child_intervals = []
        for child in (node.left, node.right):
            interval = child.bounds.intersection_interval(ray, t_max=best_distance)
            if interval is not None:
                child_intervals.append((interval[0], child))
        child_intervals.sort(key=lambda item: item[0])
        for _, child in child_intervals:
            best = self._visit_node(child, ray, best, max_distance)
        return best

    def closest_hit(self, ray, max_distance=math.inf):
        best = None

        # Fallback objects are evaluated first so they can also tighten BVH pruning.
        for index, obj in self.unbounded:
            intersection = obj.intercepts(ray)
            if not intersection["result"]:
                continue
            distance = _hit_distance(ray, intersection)
            best_distance = max_distance if best is None else best[2]
            best_index = math.inf if best is None else best[3]
            if distance <= max_distance and _candidate_is_closer(
                distance, index, best_distance, best_index
            ):
                best = (obj, intersection, distance, index)

        return self._visit_node(self.root, ray, best, max_distance)
