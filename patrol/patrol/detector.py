"""Target detectors.

Every detector has the same shape: give it a camera frame (and the drone's
state at that moment) and it returns a list of Detection objects in pixel
coordinates. The mission code doesn't care how the target was found, so you
can swap detectors without touching it:

* SimulatedDetector: no camera. It knows where the target "really" is and
  reports it whenever it would be inside the camera's view. Use it in SITL to
  test the whole patrol before the hardware is ready.
* ArucoDetector: finds a printed ArUco marker with OpenCV. The first real one.
* Later: a colour-blob detector, or a small neural network (YOLO) for
  "a person", "a car" and so on.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Protocol

from .geo import to_local
from .geolocate import CameraModel, ground_to_pixel


@dataclass
class Detection:
    u: float            # pixel column of the target's centre
    v: float            # pixel row of the target's centre
    size_px: float      # rough width of the target in pixels
    label: str = "target"
    confidence: float = 1.0


@dataclass
class VehicleState:
    lat: float
    lon: float
    alt_m: float        # height above home
    roll: float = 0.0   # radians
    pitch: float = 0.0
    yaw: float = 0.0


class Detector(Protocol):
    def detect(self, frame, state: VehicleState) -> list[Detection]: ...


class SimulatedDetector:
    """Pretends to see a target placed at a known GPS position.

    It projects the target into the simulated camera image using the drone's
    real (SITL) position and attitude, so tilting, turning and climbing all
    behave the way they will with a real camera. To be a little more honest it
    also misses some frames, adds pixel noise, and can't see targets that would
    be too small in the image.
    """

    def __init__(self, target_lat: float, target_lon: float, cam: CameraModel,
                 target_size_m: float = 0.5, min_size_px: float = 15.0,
                 hit_rate: float = 0.85, noise_px: float = 2.0, seed: int | None = None):
        self.target_lat = target_lat
        self.target_lon = target_lon
        self.cam = cam
        self.target_size_m = target_size_m
        self.min_size_px = min_size_px
        self.hit_rate = hit_rate
        self.noise_px = noise_px
        self.rng = random.Random(seed)

    def detect(self, frame, state: VehicleState) -> list[Detection]:
        if state.alt_m < 1.0:
            return []
        north, east = to_local(state.lat, state.lon, self.target_lat, self.target_lon)
        px = ground_to_pixel(north, east, state.alt_m, self.cam, state.roll, state.pitch, state.yaw)
        if px is None:
            return []
        u, v = px
        if not (0 <= u < self.cam.width and 0 <= v < self.cam.height):
            return []
        slant = math.sqrt(north ** 2 + east ** 2 + state.alt_m ** 2)
        size_px = self.target_size_m / slant * self.cam.fx
        if size_px < self.min_size_px or self.rng.random() > self.hit_rate:
            return []
        u += self.rng.gauss(0, self.noise_px)
        v += self.rng.gauss(0, self.noise_px)
        return [Detection(u, v, size_px, "sim-target", 1.0)]


class ArucoDetector:
    """Finds ArUco markers in a camera frame with OpenCV.

    Print a marker from the DICT_4X4_50 dictionary (for example at
    https://chev.me/arucogen/), as big as you can: about 50 cm across is
    comfortable from 10-15 m up with a 640x480 image.
    """

    def __init__(self, marker_id: int | None = None, dictionary: str = "DICT_4X4_50"):
        import cv2  # imported here so the rest of the package works without OpenCV

        self.cv2 = cv2
        d = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dictionary))
        self.detector = cv2.aruco.ArucoDetector(d, cv2.aruco.DetectorParameters())
        self.marker_id = marker_id

    def detect(self, frame, state: VehicleState) -> list[Detection]:
        gray = frame if frame.ndim == 2 else self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)
        found: list[Detection] = []
        if ids is None:
            return found
        for c, marker in zip(corners, ids.flatten()):
            if self.marker_id is not None and int(marker) != self.marker_id:
                continue
            pts = c.reshape(4, 2)
            u, v = pts.mean(axis=0)
            side = sum(math.dist(pts[i], pts[(i + 1) % 4]) for i in range(4)) / 4
            found.append(Detection(float(u), float(v), float(side), f"aruco-{int(marker)}", 1.0))
        return found
