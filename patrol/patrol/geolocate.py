"""Where on the ground is the thing in the picture?

Turns a pixel position in a downward-facing camera image into a north/east
offset from the drone, and back again. Assumes:

* the camera points straight down when the drone is level,
* the top edge of the image faces the drone's nose,
* the ground under the drone is flat,
* `alt_m` is height above that ground (ArduPilot's relative altitude is height
  above home, which is fine on flat fields).

Frames used:
  NED    north, east, down (the world)
  body   forward, right, down (the drone)
  camera OpenCV convention: x right in the image, y down in the image,
         z out of the lens
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CameraModel:
    """A simple pinhole camera. Defaults are the Raspberry Pi Camera v2 (IMX219)
    at 640x480 using the full sensor field of view. Replace them with your own
    calibration (fx, fy, cx, cy) when you have it."""

    width: int = 640
    height: int = 480
    hfov_deg: float = 62.2
    vfov_deg: float = 48.8

    @property
    def fx(self) -> float:
        return (self.width / 2) / math.tan(math.radians(self.hfov_deg) / 2)

    @property
    def fy(self) -> float:
        return (self.height / 2) / math.tan(math.radians(self.vfov_deg) / 2)

    @property
    def cx(self) -> float:
        return self.width / 2

    @property
    def cy(self) -> float:
        return self.height / 2


def _body_to_ned(roll: float, pitch: float, yaw: float):
    """Rotation matrix (3x3 list) from body FRD to NED, for angles in radians."""
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return [
        [cp * cy, sr * sp * cy - cr * sy, cr * sp * cy + sr * sy],
        [cp * sy, sr * sp * sy + cr * cy, cr * sp * sy - sr * cy],
        [-sp, sr * cp, cr * cp],
    ]


def _mul(m, v):
    return [sum(m[i][j] * v[j] for j in range(3)) for i in range(3)]


def _mul_t(m, v):
    """Multiply by the transpose of m (the inverse of a rotation)."""
    return [sum(m[j][i] * v[j] for j in range(3)) for i in range(3)]


def pixel_to_ground(u: float, v: float, alt_m: float, cam: CameraModel,
                    roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0) -> tuple[float, float] | None:
    """North/east offset in metres from the drone to the ground point seen at pixel (u, v).

    Angles in radians (as MAVLink's ATTITUDE message gives them). Returns None if
    the pixel's ray never reaches the ground (pointing at or above the horizon).
    """
    xc = (u - cam.cx) / cam.fx
    yc = (v - cam.cy) / cam.fy
    ray_body = [-yc, xc, 1.0]          # forward, right, down
    n, e, d = _mul(_body_to_ned(roll, pitch, yaw), ray_body)
    if d <= 1e-6:
        return None
    scale = alt_m / d
    return n * scale, e * scale


def ground_to_pixel(north: float, east: float, alt_m: float, cam: CameraModel,
                    roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0) -> tuple[float, float] | None:
    """Pixel (u, v) where a ground point `north`/`east` metres from the drone appears.

    Returns None if the point is behind the camera. The pixel can be outside the
    image; check it against cam.width / cam.height.
    """
    f, r, d = _mul_t(_body_to_ned(roll, pitch, yaw), [north, east, alt_m])
    if d <= 1e-6:
        return None
    xc, yc = r / d, -f / d
    return cam.cx + cam.fx * xc, cam.cy + cam.fy * yc
