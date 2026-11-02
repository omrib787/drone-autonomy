"""Command line entry point:  python -m patrol.run --help

SITL, with a simulated target (no camera needed):
    python -m patrol.run --connect udp:127.0.0.1:14551 --area areas/sitl_field.json \
        --sim-target -35.36245,149.16500

Real drone, from the Pi, looking for ArUco marker 7:
    python -m patrol.run --connect /dev/serial0 --baud 921600 --area areas/my_field.json \
        --camera pi --aruco 7 --wait-for-guided
"""
from __future__ import annotations

import argparse
import json

from .camera import NoCamera, OpenCVCamera, PiCamera
from .detector import ArucoDetector, SimulatedDetector
from .geolocate import CameraModel
from .mission import MissionConfig, PatrolMission
from .vehicle import Vehicle


def main() -> None:
    p = argparse.ArgumentParser(description="Search an area with a lawnmower pattern until the camera finds a target.")
    p.add_argument("--connect", default="udp:127.0.0.1:14551", help="MAVLink connection string")
    p.add_argument("--baud", type=int, default=921600, help="serial baud rate (ignored for UDP/TCP)")
    p.add_argument("--area", required=True, help="JSON file with the area's corners (see areas/)")
    p.add_argument("--alt", type=float, default=15.0, help="search altitude in metres above home")
    p.add_argument("--speed", type=float, default=3.0, help="search speed in m/s")
    p.add_argument("--overlap", type=float, default=0.3, help="overlap between neighbouring lanes, 0-1")
    p.add_argument("--heading", type=float, default=None, help="lane direction in degrees (default: longest edge)")
    p.add_argument("--target-size", type=float, default=0.5, help="target width in metres")
    p.add_argument("--on-found", choices=["rtl", "hover", "land"], default="rtl")
    p.add_argument("--wait-for-guided", action="store_true",
                   help="don't arm or take off: wait for the pilot to fly up and switch to GUIDED")
    p.add_argument("--sim-target", help="LAT,LON of a pretend target (SITL testing)")
    p.add_argument("--camera", choices=["pi", "webcam"], help="real camera to use")
    p.add_argument("--aruco", type=int, default=None, help="ArUco marker id to look for (any id if omitted)")
    p.add_argument("--result", default="patrol_result.json", help="where to write the result")
    a = p.parse_args()

    with open(a.area) as f:
        area = json.load(f)
    corners = [tuple(pt) for pt in area["corners"]]

    cam = CameraModel()
    if a.sim_target:
        lat, lon = (float(x) for x in a.sim_target.split(","))
        detector = SimulatedDetector(lat, lon, cam, target_size_m=a.target_size)
        camera = NoCamera()
    elif a.camera:
        detector = ArucoDetector(a.aruco)
        camera = PiCamera(cam.width, cam.height) if a.camera == "pi" else OpenCVCamera(0, cam.width, cam.height)
    else:
        p.error("choose --sim-target (SITL) or --camera (real camera)")

    cfg = MissionConfig(area=corners, alt_m=a.alt, speed_m_s=a.speed, overlap=a.overlap,
                        heading_deg=a.heading, target_size_m=a.target_size, on_found=a.on_found,
                        wait_for_guided=a.wait_for_guided, result_file=a.result)

    vehicle = Vehicle(a.connect, a.baud)
    vehicle.connect()
    try:
        result = PatrolMission(vehicle, detector, camera, cam, cfg).run()
    finally:
        camera.close()

    if result.found and a.sim_target:
        from .geo import distance_m
        err = distance_m(result.lat, result.lon, lat, lon)
        print(f"Simulated target was at {lat}, {lon}: estimate is {err:.1f} m off")


if __name__ == "__main__":
    main()
