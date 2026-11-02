"""Camera sources. Each has read() returning an image (a numpy array) or None.

* NoCamera: for SITL with the SimulatedDetector, which doesn't need pictures.
* PiCamera: the Raspberry Pi camera through picamera2 (Raspberry Pi OS).
* OpenCVCamera: any webcam OpenCV can open, handy for testing on a laptop.
"""
from __future__ import annotations


class NoCamera:
    def read(self):
        return None

    def close(self) -> None:
        pass


class PiCamera:
    def __init__(self, width: int = 640, height: int = 480):
        from picamera2 import Picamera2

        self.cam = Picamera2()
        config = self.cam.create_video_configuration(main={"size": (width, height), "format": "RGB888"})
        self.cam.configure(config)
        self.cam.start()

    def read(self):
        return self.cam.capture_array()  # picamera2's "RGB888" is BGR byte order, which OpenCV expects

    def close(self) -> None:
        self.cam.stop()


class OpenCVCamera:
    def __init__(self, index: int = 0, width: int = 640, height: int = 480):
        import cv2

        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read(self):
        ok, frame = self.cap.read()
        return frame if ok else None

    def close(self) -> None:
        self.cap.release()
