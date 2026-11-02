"""Unit tests for the maths. Run from the patrol/ folder:  python -m pytest"""
import math
import random

import pytest

from patrol.coverage import (camera_footprint, is_convex, lane_spacing, lawnmower,
                             longest_edge_heading, path_length, target_size_px)
from patrol.detector import SimulatedDetector, VehicleState
from patrol.geo import distance_m, to_global, to_local
from patrol.geolocate import CameraModel, ground_to_pixel, pixel_to_ground

HOME = (-35.363262, 149.165237)


def test_local_global_round_trip():
    lat, lon = to_global(*HOME, 120.0, -45.0)
    n, e = to_local(*HOME, lat, lon)
    assert n == pytest.approx(120.0, abs=1e-6)
    assert e == pytest.approx(-45.0, abs=1e-6)
    assert distance_m(*HOME, lat, lon) == pytest.approx(math.hypot(120, 45), abs=1e-6)


def test_footprint_pi_camera_v2():
    w, h = camera_footprint(20, 62.2, 48.8)
    assert w == pytest.approx(24.1, abs=0.1)
    assert h == pytest.approx(18.1, abs=0.1)


def test_lane_spacing_and_target_pixels():
    assert lane_spacing(20, 62.2, 0.3) == pytest.approx(0.7 * 24.13, abs=0.1)
    # A 0.5 m target from 15 m up in a 640 px wide image is about 18 px.
    assert target_size_px(0.5, 15, 62.2, 640) == pytest.approx(17.8, abs=0.5)


def test_convexity():
    assert is_convex([(0, 0), (0, 10), (10, 10), (10, 0)])
    assert not is_convex([(0, 0), (0, 10), (5, 5), (10, 10), (10, 0)])


def test_lawnmower_rectangle_covers_every_lane():
    rect = [(0, 0), (0, 60), (40, 60), (40, 0)]           # 40 m north-south, 60 m east-west
    wps = lawnmower(rect, spacing_m=10, heading_deg=90)   # lanes run east-west
    assert len(wps) == 8                                  # 4 lanes x 2 ends
    norths = sorted({round(n, 6) for n, _ in wps})
    assert norths == [5, 15, 25, 35]
    # Lanes alternate direction: the end of one lane is next to the start of the next.
    for i in range(1, len(wps) - 1, 2):
        assert math.dist(wps[i], wps[i + 1]) == pytest.approx(10, abs=1e-6)
    # Every waypoint is inside the rectangle.
    for n, e in wps:
        assert -1e-6 <= n <= 40 + 1e-6 and -1e-6 <= e <= 60 + 1e-6


def test_lawnmower_rejects_concave():
    with pytest.raises(ValueError):
        lawnmower([(0, 0), (0, 10), (5, 5), (10, 10), (10, 0)], 2)


def test_longest_edge_heading_and_length():
    rect = [(0, 0), (0, 60), (40, 60), (40, 0)]
    assert longest_edge_heading(rect) == pytest.approx(90)
    assert path_length([(0, 0), (3, 4)], start=(0, -5)) == pytest.approx(10)


@pytest.mark.parametrize("roll,pitch,yaw", [(0, 0, 0), (0.1, -0.05, 1.2), (-0.08, 0.12, -2.5)])
def test_pixel_ground_round_trip(roll, pitch, yaw):
    cam = CameraModel()
    rng = random.Random(1)
    for _ in range(50):
        n, e = rng.uniform(-6, 6), rng.uniform(-6, 6)
        px = ground_to_pixel(n, e, 15, cam, roll, pitch, yaw)
        assert px is not None
        back = pixel_to_ground(*px, 15, cam, roll, pitch, yaw)
        assert back[0] == pytest.approx(n, abs=1e-6)
        assert back[1] == pytest.approx(e, abs=1e-6)


def test_image_orientation():
    """Image top faces the nose; image right faces the right wing."""
    cam = CameraModel()
    u, v = ground_to_pixel(3, 0, 15, cam, yaw=0)    # 3 m north, drone facing north
    assert u == pytest.approx(cam.cx) and v < cam.cy
    u, v = ground_to_pixel(0, 3, 15, cam, yaw=0)    # 3 m east
    assert u > cam.cx and v == pytest.approx(cam.cy)
    u, v = ground_to_pixel(0, 3, 15, cam, yaw=math.pi / 2)   # facing east: east is "ahead"
    assert v < cam.cy and u == pytest.approx(cam.cx, abs=1e-6)


def test_simulated_detector_sees_only_nearby_targets():
    cam = CameraModel()
    target = to_global(*HOME, 4.0, 2.0)
    det = SimulatedDetector(*target, cam, hit_rate=1.0, noise_px=0.0, seed=0)
    above = VehicleState(*HOME, alt_m=15)
    hits = det.detect(None, above)
    assert len(hits) == 1
    n, e = pixel_to_ground(hits[0].u, hits[0].v, 15, cam)
    assert (n, e) == (pytest.approx(4.0, abs=1e-6), pytest.approx(2.0, abs=1e-6))
    far = VehicleState(*to_global(*HOME, 60, 60), alt_m=15)
    assert det.detect(None, far) == []
    too_high = VehicleState(*HOME, alt_m=40)                  # 0.5 m target is under 15 px from 40 m
    assert det.detect(None, too_high) == []
