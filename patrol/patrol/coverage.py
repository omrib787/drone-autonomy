"""Coverage planning: a "lawnmower" (boustrophedon) path over an area.

The drone flies parallel lanes across the area, turning at each end, like
mowing a lawn. Lane spacing comes from how much ground the camera sees at the
search altitude, minus some overlap so nothing slips between two lanes.

All coordinates here are local metres: (north, east). Use geo.py to convert
GPS points in and out.

Limitation: the area must be convex (a rectangle, a triangle, most fields).
Split an L-shaped area into convex pieces and search them one after another.
"""
from __future__ import annotations

import math

Point = tuple[float, float]  # (north_m, east_m)


def camera_footprint(alt_m: float, hfov_deg: float, vfov_deg: float) -> tuple[float, float]:
    """Ground area seen by a camera pointing straight down: (width_m, height_m).

    Width is along the image's horizontal axis, height along its vertical axis.
    """
    width = 2 * alt_m * math.tan(math.radians(hfov_deg) / 2)
    height = 2 * alt_m * math.tan(math.radians(vfov_deg) / 2)
    return width, height


def lane_spacing(alt_m: float, hfov_deg: float, overlap: float = 0.3) -> float:
    """Distance between lanes so neighbouring camera strips overlap by `overlap` (0-1).

    Assumes the image's horizontal axis points across the lanes, which is true
    when the camera's top edge faces the drone's nose and the drone flies along
    the lane.
    """
    if not 0 <= overlap < 1:
        raise ValueError("overlap must be between 0 and 1")
    width, _ = camera_footprint(alt_m, hfov_deg, 1.0)
    return width * (1 - overlap)


def target_size_px(target_m: float, alt_m: float, hfov_deg: float, image_width_px: int) -> float:
    """How many pixels wide a target of `target_m` metres appears from `alt_m` up.

    Detectors need roughly 15-20 px across a target to find it reliably, so use
    this to choose the search altitude and the size of the thing you search for.
    """
    width_m, _ = camera_footprint(alt_m, hfov_deg, 1.0)
    return target_m / width_m * image_width_px


def _rotate(p: Point, heading_deg: float) -> Point:
    """Rotate (north, east) into (along, across) for lanes pointing at heading_deg."""
    h = math.radians(heading_deg)
    north, east = p
    along = north * math.cos(h) + east * math.sin(h)
    across = -north * math.sin(h) + east * math.cos(h)
    return along, across


def _unrotate(p: Point, heading_deg: float) -> Point:
    """Inverse of _rotate: (along, across) back to (north, east)."""
    h = math.radians(heading_deg)
    along, across = p
    north = along * math.cos(h) - across * math.sin(h)
    east = along * math.sin(h) + across * math.cos(h)
    return north, east


def is_convex(polygon: list[Point]) -> bool:
    """True if the polygon (in order, either direction) has no inward corners."""
    n = len(polygon)
    if n < 3:
        return False
    sign = 0
    for i in range(n):
        ax, ay = polygon[i]
        bx, by = polygon[(i + 1) % n]
        cx, cy = polygon[(i + 2) % n]
        cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if abs(cross) < 1e-9:
            continue
        s = 1 if cross > 0 else -1
        if sign == 0:
            sign = s
        elif s != sign:
            return False
    return sign != 0


def lawnmower(polygon: list[Point], spacing_m: float, heading_deg: float = 0.0) -> list[Point]:
    """Waypoints for a lawnmower sweep of a convex polygon.

    polygon:     corners in local metres (north, east), in order around the edge.
    spacing_m:   distance between lanes (see lane_spacing()).
    heading_deg: direction the lanes run, in degrees clockwise from north.
                 Lanes along the longest edge mean fewer turns.

    Returns the waypoints in flying order. Each lane contributes two points
    (its start and end); consecutive lanes alternate direction. The first lane
    sits half a spacing in from the edge, so the camera strip just reaches it.
    """
    if spacing_m <= 0:
        raise ValueError("spacing_m must be positive")
    if not is_convex(polygon):
        raise ValueError("area must be convex; split it into convex pieces")

    rotated = [_rotate(p, heading_deg) for p in polygon]
    acrosses = [p[1] for p in rotated]
    lo, hi = min(acrosses), max(acrosses)

    waypoints: list[Point] = []
    lane = 0
    c = lo + spacing_m / 2
    # Always include at least one lane, even for an area narrower than one spacing.
    if c > hi:
        c = (lo + hi) / 2
    while c <= hi + 1e-9:
        crossings = []
        n = len(rotated)
        for i in range(n):
            (a1, c1), (a2, c2) = rotated[i], rotated[(i + 1) % n]
            if (c1 - c) * (c2 - c) <= 0 and c1 != c2:
                t = (c - c1) / (c2 - c1)
                crossings.append(a1 + t * (a2 - a1))
        if len(crossings) >= 2:
            start, end = min(crossings), max(crossings)
            if lane % 2 == 1:
                start, end = end, start
            waypoints.append(_unrotate((start, c), heading_deg))
            waypoints.append(_unrotate((end, c), heading_deg))
            lane += 1
        c += spacing_m
    return waypoints


def longest_edge_heading(polygon: list[Point]) -> float:
    """Heading (degrees from north) of the polygon's longest edge: a good lane direction."""
    best_len, best_heading = -1.0, 0.0
    n = len(polygon)
    for i in range(n):
        (n1, e1), (n2, e2) = polygon[i], polygon[(i + 1) % n]
        length = math.hypot(n2 - n1, e2 - e1)
        if length > best_len:
            best_len = length
            best_heading = math.degrees(math.atan2(e2 - e1, n2 - n1)) % 180
    return best_heading


def path_length(points: list[Point], start: Point | None = None) -> float:
    """Total length of a path through the points, optionally starting from `start`."""
    pts = ([start] if start is not None else []) + list(points)
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
