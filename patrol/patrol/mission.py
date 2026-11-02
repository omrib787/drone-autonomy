"""The patrol mission: a small state machine.

    PREFLIGHT -> TAKEOFF -> SEARCH -> CONFIRM -> LOCATE -> FINISH
                              |                              ^
                              +------ area covered ----------+

PREFLIGHT  plan the lawnmower path, check it against the safety limits
TAKEOFF    arm and climb (SITL), or wait for the pilot to switch to GUIDED
SEARCH     fly the lanes, running the detector on every frame
CONFIRM    the detector fired: keep looking until enough frames agree
LOCATE     stop, fly over the estimate, refine it with more detections
FINISH     report the position, then RTL / hover / land

At every step, if the pilot switches out of GUIDED (flicks the mode switch),
the script stops sending commands immediately. The pilot always wins.
"""
from __future__ import annotations

import json
import math
import statistics
import time
from collections import deque
from dataclasses import asdict, dataclass, field

from .coverage import lane_spacing, lawnmower, longest_edge_heading, path_length, target_size_px
from .detector import Detection, Detector
from .geo import distance_m, to_global, to_local
from .geolocate import CameraModel, pixel_to_ground
from .vehicle import Vehicle


@dataclass
class MissionConfig:
    area: list[tuple[float, float]]          # (lat, lon) corners, in order
    alt_m: float = 15.0                      # search height above home
    speed_m_s: float = 3.0                   # slow enough to avoid motion blur
    overlap: float = 0.3                     # sideways overlap between camera strips
    heading_deg: float | None = None         # lane direction; None = along the longest edge
    target_size_m: float = 0.5               # only used to print the detectability estimate
    confirm_hits: int = 4                    # this many detections ...
    confirm_window: int = 10                 # ... within this many frames confirms a target
    locate_s: float = 4.0                    # hover this long over the target to refine its position
    on_found: str = "rtl"                    # "rtl", "hover" or "land"
    wait_for_guided: bool = False            # real drone: pilot takes off, then switches to GUIDED
    max_alt_m: float = 45.0                  # Israel's limit is 50 m; keep a margin
    max_range_m: float = 250.0               # every corner of the area must be this close to home
    battery_rtl_pct: int = 30                # return home below this battery percentage
    timeout_s: float = 900.0
    result_file: str = "patrol_result.json"


@dataclass
class Sighting:
    lat: float
    lon: float
    t: float
    size_px: float


@dataclass
class Result:
    found: bool
    reason: str
    lat: float | None = None
    lon: float | None = None
    sightings: int = 0
    spread_m: float | None = None
    flight_time_s: float = 0.0
    extra: dict = field(default_factory=dict)


class Abort(Exception):
    """Raised when the pilot takes over or a safety limit trips."""


class PatrolMission:
    def __init__(self, vehicle: Vehicle, detector: Detector, camera, cam: CameraModel, cfg: MissionConfig):
        self.v = vehicle
        self.detector = detector
        self.camera = camera
        self.cam = cam
        self.cfg = cfg
        self.start_time = time.time()
        self.in_air_under_script = False
        self.sightings: list[Sighting] = []

    # ---------- helpers ----------

    def log(self, msg: str) -> None:
        print(f"[{time.time() - self.start_time:6.1f}s] {msg}")

    def look(self) -> Detection | None:
        """Grab a frame, run the detector, and return the biggest detection (or None)."""
        state = self.v.state()
        found = self.detector.detect(self.camera.read(), state)
        if not found:
            return None
        best = max(found, key=lambda d: d.size_px)
        offset = pixel_to_ground(best.u, best.v, state.alt_m, self.cam, state.roll, state.pitch, state.yaw)
        if offset is not None:
            lat, lon = to_global(state.lat, state.lon, *offset)
            self.sightings.append(Sighting(lat, lon, time.time(), best.size_px))
        return best

    def check_safety(self) -> None:
        """Called every loop once we're flying under script control."""
        if self.v.mode != "GUIDED":
            raise Abort(f"pilot switched to {self.v.mode}; script stopped sending commands")
        if 0 <= self.v.battery_pct < self.cfg.battery_rtl_pct:
            raise Abort(f"battery at {self.v.battery_pct}%")
        if time.time() - self.start_time > self.cfg.timeout_s:
            raise Abort("mission timeout")

    def estimate(self, since: float = 0.0) -> tuple[float, float, float] | None:
        """Median position of the sightings after `since`, and their spread in metres."""
        pts = [s for s in self.sightings if s.t >= since]
        if not pts:
            return None
        lat = statistics.median(s.lat for s in pts)
        lon = statistics.median(s.lon for s in pts)
        spread = max(distance_m(lat, lon, s.lat, s.lon) for s in pts)
        return lat, lon, spread

    # ---------- phases ----------

    def plan(self) -> list[tuple[float, float]]:
        cfg = self.cfg
        self.v.wait(lambda: self.v.lat != 0.0, 30, "a position")
        try:
            self.v.wait(lambda: self.v.home is not None, 10, "the home position")
        except TimeoutError:
            self.v.home = (self.v.lat, self.v.lon)
            self.log("no HOME_POSITION yet; using the current position as home")
        home_lat, home_lon = self.v.home

        if cfg.alt_m > cfg.max_alt_m:
            raise ValueError(f"search altitude {cfg.alt_m} m is above the {cfg.max_alt_m} m limit")
        local = [to_local(home_lat, home_lon, lat, lon) for lat, lon in cfg.area]
        far = max(math.hypot(n, e) for n, e in local)
        if far > cfg.max_range_m:
            raise ValueError(f"area reaches {far:.0f} m from home; the limit is {cfg.max_range_m:.0f} m")

        heading = cfg.heading_deg if cfg.heading_deg is not None else longest_edge_heading(local)
        spacing = lane_spacing(cfg.alt_m, self.cam.hfov_deg, cfg.overlap)
        wps_local = lawnmower(local, spacing, heading)
        length = path_length(wps_local, start=(0.0, 0.0))
        px = target_size_px(cfg.target_size_m, cfg.alt_m, self.cam.hfov_deg, self.cam.width)

        self.log(f"Plan: {len(wps_local) // 2} lanes, {spacing:.1f} m apart, heading {heading:.0f} deg")
        self.log(f"      {length:.0f} m of flying, about {length / cfg.speed_m_s / 60:.1f} min at {cfg.speed_m_s} m/s")
        self.log(f"      a {cfg.target_size_m} m target will be about {px:.0f} px wide at {cfg.alt_m} m")
        if px < 15:
            self.log("      WARNING: that's small for reliable detection; fly lower or use a bigger target")
        return [to_global(home_lat, home_lon, n, e) for n, e in wps_local]

    def takeoff(self) -> None:
        cfg = self.cfg
        if cfg.wait_for_guided:
            self.log("Waiting for you to take off and switch to GUIDED ...")
            self.v.wait(lambda: self.v.mode == "GUIDED" and self.v.armed and self.v.alt_m > 2.0,
                        600, "GUIDED, armed and above 2 m")
            self.in_air_under_script = True
            self.log(f"GUIDED at {self.v.alt_m:.1f} m: starting the patrol")
            return
        self.v.wait(lambda: self.v.mode != "", 5, "the flight mode")
        if self.v.armed:
            raise Abort("the drone is already armed: land it first, or use --wait-for-guided to start mid-air")
        self.log("Waiting until the autopilot is ready to arm ...")
        self.v.wait(lambda: self.v.ready_to_arm and self.v.gps_fix >= 3, 180, "ready to arm with a 3D GPS fix")
        self.v.set_mode("GUIDED")
        self.v.arm()
        self.in_air_under_script = True
        self.log(f"Armed. Taking off to {cfg.alt_m} m")
        self.v.takeoff(cfg.alt_m)
        end = time.time() + 60
        while self.v.alt_m < cfg.alt_m * 0.9:
            self.v.update()
            self.check_safety()
            if time.time() > end:
                raise Abort("takeoff took too long")
            time.sleep(0.1)

    def fly_to(self, lat: float, lon: float, speed: float, hits: deque | None, accept_m: float = 2.0) -> bool:
        """Fly to a point at `speed` m/s. While flying, watch for the target if `hits` is given.

        Returns True if the target was confirmed on the way, False on arrival.
        """
        last_send = 0.0
        while True:
            self.v.update()
            self.check_safety()
            if time.time() - last_send > 1.0:
                # Repeat both commands every second in case one gets lost. The speed
                # has to come after the first position target: switching GUIDED into
                # waypoint control resets the speed to the WPNAV default.
                self.v.goto(lat, lon, self.cfg.alt_m)
                self.v.set_speed(speed)
                last_send = time.time()
            if hits is not None:
                hits.append(self.look() is not None)
                if sum(hits) >= self.cfg.confirm_hits:
                    return True
            if distance_m(self.v.lat, self.v.lon, lat, lon) < accept_m:
                return False
            time.sleep(0.1)

    def search(self, waypoints) -> bool:
        hits: deque = deque(maxlen=self.cfg.confirm_window)
        for i, (lat, lon) in enumerate(waypoints):
            lane, end = divmod(i, 2)
            self.log(f"Lane {lane + 1}, {'end' if end else 'start'}: heading to {lat:.6f}, {lon:.6f}")
            if self.fly_to(lat, lon, self.cfg.speed_m_s, hits):
                self.log(f"Target confirmed ({sum(hits)} of the last {len(hits)} frames)")
                return True
        return False

    def locate(self) -> tuple[float, float, float] | None:
        self.v.hold()
        first = self.estimate()
        if first is None:
            return None
        lat, lon, _ = first
        self.log(f"First estimate {lat:.6f}, {lon:.6f}: flying over it")
        self.fly_to(lat, lon, 1.5, None, accept_m=1.0)
        refine_start = time.time()
        while time.time() - refine_start < self.cfg.locate_s:
            self.v.update()
            self.check_safety()
            self.look()
            time.sleep(0.1)
        return self.estimate(since=refine_start) or first

    def finish(self, result: Result) -> None:
        result.flight_time_s = round(time.time() - self.start_time, 1)
        with open(self.cfg.result_file, "w") as f:
            json.dump(asdict(result), f, indent=2)
        self.log(f"Result written to {self.cfg.result_file}")

    def leave(self, how: str) -> None:
        if how == "rtl":
            self.log("Returning home (RTL)")
            self.v.set_mode("RTL")
        elif how == "land":
            self.log("Landing here (LAND)")
            self.v.set_mode("LAND")
        else:
            self.log("Hovering in GUIDED. Take over with the mode switch")

    # ---------- the whole thing ----------

    def run(self) -> Result:
        waypoints = self.plan()
        try:
            self.takeoff()
            if not self.search(waypoints):
                self.log("Area covered without a confirmed target")
                result = Result(False, "area covered, nothing found")
                self.leave("rtl")
            else:
                est = self.locate()
                if est is None:
                    result = Result(False, "lost the target while locating it")
                    self.leave("rtl")
                else:
                    lat, lon, spread = est
                    self.log(f"TARGET at {lat:.7f}, {lon:.7f} (sightings agree within {spread:.1f} m)")
                    result = Result(True, "target found", lat, lon, len(self.sightings), round(spread, 2))
                    self.leave(self.cfg.on_found)
        except Abort as e:
            self.log(f"ABORT: {e}")
            result = Result(False, f"aborted: {e}")
            if self.v.mode == "GUIDED" and self.in_air_under_script:
                self.leave("rtl")
        except KeyboardInterrupt:
            self.log("Stopped from the keyboard")
            result = Result(False, "stopped from the keyboard")
            if self.v.mode == "GUIDED" and self.in_air_under_script:
                self.leave("rtl")
        self.finish(result)
        return result
