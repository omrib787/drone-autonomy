"""Small-area geometry: convert between GPS coordinates and local metres.

Everything in the patrol code plans in a flat "local" frame measured in metres
from a reference point (usually home): north is +x, east is +y. That keeps the
maths simple. Over a field a few hundred metres across, the flat-earth error is
a few centimetres, far smaller than GPS error.
"""
from __future__ import annotations

import math

EARTH_RADIUS_M = 6_378_137.0  # WGS-84 equatorial radius


def to_local(ref_lat: float, ref_lon: float, lat: float, lon: float) -> tuple[float, float]:
    """Return (north_m, east_m) of a GPS point relative to a reference point."""
    north = math.radians(lat - ref_lat) * EARTH_RADIUS_M
    east = math.radians(lon - ref_lon) * EARTH_RADIUS_M * math.cos(math.radians(ref_lat))
    return north, east


def to_global(ref_lat: float, ref_lon: float, north: float, east: float) -> tuple[float, float]:
    """Inverse of to_local: return (lat, lon) of a point given in metres from the reference."""
    lat = ref_lat + math.degrees(north / EARTH_RADIUS_M)
    lon = ref_lon + math.degrees(east / (EARTH_RADIUS_M * math.cos(math.radians(ref_lat))))
    return lat, lon


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Horizontal distance between two nearby GPS points, in metres."""
    north, east = to_local(lat1, lon1, lat2, lon2)
    return math.hypot(north, east)
