"""A thin, readable wrapper around pymavlink for the few things the patrol needs.

It keeps the latest copy of the drone's state (position, attitude, mode,
battery) up to date from incoming MAVLink messages, and sends the handful of
commands we use: change mode, arm, take off, fly to a point, set speed.

Works the same against SITL on a laptop and against the real flight
controller over the Pi's serial port: only the connection string changes.
"""
from __future__ import annotations

import math
import time

from pymavlink import mavutil

from .detector import VehicleState

# Ask the flight controller to send these messages at these rates (Hz).
STREAMS = {
    "HEARTBEAT": 1,
    "GLOBAL_POSITION_INT": 10,
    "ATTITUDE": 10,
    "SYS_STATUS": 2,
    "GPS_RAW_INT": 2,
    "HOME_POSITION": 0.5,
}

PREARM_CHECK_BIT = mavutil.mavlink.MAV_SYS_STATUS_PREARM_CHECK  # "ready to arm" flag


class Vehicle:
    def __init__(self, url: str, baud: int = 921600):
        self.m = mavutil.mavlink_connection(url, baud=baud, source_component=191)
        self.lat = self.lon = 0.0
        self.alt_m = 0.0
        self.roll = self.pitch = self.yaw = 0.0
        self.mode = ""
        self.armed = False
        self.battery_pct = -1
        self.gps_fix = 0
        self.ready_to_arm = False
        self.home: tuple[float, float] | None = None
        self.last_text = ""

    # ---------- connection and state ----------

    def connect(self, timeout: float = 30) -> None:
        print(f"Waiting for a heartbeat on {self.m.address} ...")
        hb = self.m.wait_heartbeat(timeout=timeout)
        if hb is None:
            raise TimeoutError("no heartbeat: check the connection string and that the drone or SITL is running")
        print(f"Connected to system {self.m.target_system}, component {self.m.target_component}")
        for name, hz in STREAMS.items():
            msg_id = getattr(mavutil.mavlink, f"MAVLINK_MSG_ID_{name}")
            self.command(mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, msg_id, int(1e6 / hz))
        self.command(mavutil.mavlink.MAV_CMD_GET_HOME_POSITION)

    def update(self) -> None:
        """Read every message waiting and update the state. Call this often."""
        while True:
            msg = self.m.recv_match(blocking=False)
            if msg is None:
                return
            t = msg.get_type()
            if t == "GLOBAL_POSITION_INT":
                self.lat, self.lon = msg.lat / 1e7, msg.lon / 1e7
                self.alt_m = msg.relative_alt / 1000
            elif t == "ATTITUDE":
                self.roll, self.pitch, self.yaw = msg.roll, msg.pitch, msg.yaw
            elif t == "HEARTBEAT" and msg.get_srcSystem() == self.m.target_system and msg.get_srcComponent() == 1:
                self.mode = mavutil.mode_string_v10(msg)
                self.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            elif t == "SYS_STATUS":
                self.battery_pct = msg.battery_remaining
                self.ready_to_arm = bool(msg.onboard_control_sensors_health & PREARM_CHECK_BIT)
            elif t == "GPS_RAW_INT":
                self.gps_fix = msg.fix_type
            elif t == "HOME_POSITION":
                self.home = (msg.latitude / 1e7, msg.longitude / 1e7)
            elif t == "STATUSTEXT":
                self.last_text = msg.text
                print(f"  [autopilot] {msg.text}")

    def state(self) -> VehicleState:
        return VehicleState(self.lat, self.lon, self.alt_m, self.roll, self.pitch, self.yaw)

    def wait(self, condition, timeout: float, what: str) -> None:
        """Keep updating until condition() is true, or raise after `timeout` seconds."""
        end = time.time() + timeout
        while time.time() < end:
            self.update()
            if condition():
                return
            time.sleep(0.05)
        raise TimeoutError(f"timed out waiting for {what}")

    # ---------- commands ----------

    def command(self, cmd: int, *params: float) -> None:
        p = list(params) + [0.0] * (7 - len(params))
        self.m.mav.command_long_send(self.m.target_system, self.m.target_component, cmd, 0, *p)

    def set_mode(self, name: str, timeout: float = 5) -> None:
        self.m.set_mode(name)
        self.wait(lambda: self.mode == name, timeout, f"mode {name}")

    def arm(self, timeout: float = 20) -> None:
        """Arm, retrying every few seconds: right after boot the autopilot can still refuse."""
        end = time.time() + timeout
        while time.time() < end:
            self.m.arducopter_arm()
            try:
                self.wait(lambda: self.armed, 3, "arming")
                return
            except TimeoutError:
                pass
        raise TimeoutError("could not arm: read the [autopilot] messages above for the reason")

    def takeoff(self, alt_m: float) -> None:
        self.command(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, alt_m)

    def set_speed(self, m_per_s: float) -> None:
        self.command(mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 1, m_per_s, -1)

    def goto(self, lat: float, lon: float, alt_m: float) -> None:
        """Fly to a GPS point at `alt_m` above home. Only works in GUIDED mode."""
        position_only = 0b0000_1101_1111_1000  # ignore velocity, acceleration, yaw
        self.m.mav.set_position_target_global_int_send(
            0, self.m.target_system, self.m.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, position_only,
            int(lat * 1e7), int(lon * 1e7), alt_m,
            0, 0, 0, 0, 0, 0, 0, 0)

    def hold(self) -> None:
        """Stop and hover where we are (GUIDED mode)."""
        self.goto(self.lat, self.lon, self.alt_m)

    def yaw_deg(self) -> float:
        return math.degrees(self.yaw) % 360
