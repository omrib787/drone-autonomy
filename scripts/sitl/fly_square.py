"""Fly a 20 m square at 10 m altitude using local position targets, then land.

Builds on hello_mavlink.py. New ideas here:
  * LOCAL_NED coordinates: metres north/east/down from the EKF origin (near home).
    Down is positive, so 10 m up is z = -10.
  * SET_POSITION_TARGET_LOCAL_NED: "go to this point" in GUIDED mode.
  * Checking arrival with LOCAL_POSITION_NED.

Run SITL first, then:  python3 fly_square.py
"""
import math

from pymavlink import mavutil

ALT = 10      # metres
SIDE = 20     # metres
CORNERS = [(SIDE, 0), (SIDE, SIDE), (0, SIDE), (0, 0)]   # (north, east)
POSITION_ONLY = 0b0000_1101_1111_1000                    # ignore velocity, acceleration and yaw

m = mavutil.mavlink_connection("udp:127.0.0.1:14551")
m.wait_heartbeat()
print("Connected to system", m.target_system)

# Ask for local position 10 times a second.
m.mav.command_long_send(m.target_system, m.target_component,
                        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
                        mavutil.mavlink.MAVLINK_MSG_ID_LOCAL_POSITION_NED, 100_000, 0, 0, 0, 0, 0)

print("Waiting for the autopilot to be ready to arm ...")
while True:
    status = m.recv_match(type="SYS_STATUS", blocking=True, timeout=5)
    if status and status.onboard_control_sensors_health & mavutil.mavlink.MAV_SYS_STATUS_PREARM_CHECK:
        break

m.set_mode("GUIDED")
m.arducopter_arm()
m.motors_armed_wait()
m.mav.command_long_send(m.target_system, m.target_component,
                        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, ALT)
while m.recv_match(type="GLOBAL_POSITION_INT", blocking=True).relative_alt / 1000 < ALT * 0.95:
    pass
print(f"At {ALT} m, starting the square")


def go_to(north, east):
    m.mav.set_position_target_local_ned_send(
        0, m.target_system, m.target_component, mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        POSITION_ONLY, north, east, -ALT, 0, 0, 0, 0, 0, 0, 0, 0)
    while True:
        p = m.recv_match(type="LOCAL_POSITION_NED", blocking=True)
        if math.hypot(p.x - north, p.y - east) < 1.0:
            print(f"  reached corner ({north}, {east})")
            return


for north, east in CORNERS:
    go_to(north, east)

m.set_mode("LAND")
m.motors_disarmed_wait()
print("Landed and disarmed")
