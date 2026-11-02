"""Bench test for the camera and detector, without a flight controller.

Point the camera at a printed ArUco marker and watch the detections:

    python3 -m patrol.bench --camera pi --aruco 7
    python3 -m patrol.bench --camera webcam --save hit.jpg

It prints every detection with its pixel position and size, and the frame
rate, so you can check the detector is fast enough and sees the marker from
the distances you plan to fly at. Ctrl+C to stop.
"""
from __future__ import annotations

import argparse
import time

from .camera import OpenCVCamera, PiCamera
from .detector import ArucoDetector, VehicleState
from .geolocate import CameraModel, pixel_to_ground


def main() -> None:
    p = argparse.ArgumentParser(description="Run the detector on live camera frames.")
    p.add_argument("--camera", choices=["pi", "webcam"], required=True)
    p.add_argument("--aruco", type=int, default=None, help="marker id (any if omitted)")
    p.add_argument("--height", type=float, default=None,
                   help="camera height above the marker in metres; prints the marker's ground offset")
    p.add_argument("--save", help="save the first frame with a detection to this file")
    a = p.parse_args()

    cam = CameraModel()
    camera = PiCamera(cam.width, cam.height) if a.camera == "pi" else OpenCVCamera(0, cam.width, cam.height)
    detector = ArucoDetector(a.aruco)
    state = VehicleState(0.0, 0.0, a.height or 0.0)
    frames, t0, saved = 0, time.time(), False
    try:
        while True:
            frame = camera.read()
            if frame is None:
                continue
            frames += 1
            for d in detector.detect(frame, state):
                line = f"{d.label}: pixel ({d.u:.0f}, {d.v:.0f}), {d.size_px:.0f} px wide"
                if a.height:
                    n, e = pixel_to_ground(d.u, d.v, a.height, cam)
                    line += f", {n:+.2f} m forward, {e:+.2f} m right"
                print(line)
                if a.save and not saved:
                    import cv2
                    cv2.circle(frame, (int(d.u), int(d.v)), int(d.size_px / 2), (0, 0, 255), 2)
                    cv2.imwrite(a.save, frame)
                    saved = True
                    print(f"saved {a.save}")
            if time.time() - t0 >= 5:
                print(f"--- {frames / (time.time() - t0):.1f} frames per second")
                frames, t0 = 0, time.time()
    except KeyboardInterrupt:
        pass
    finally:
        camera.close()


if __name__ == "__main__":
    main()
