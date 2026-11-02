"""Your first MAVLink program: connect, arm, take off to 10 m, land.

Run SITL first (see docs/03-dev-environment.md), then in a second terminal:
    python3 hello_mavlink.py

sim_vehicle.py forwards MAVLink to UDP port 14551, which is where this listens.
"""
import time

from pymavlink import mavutil

TAKEOFF_ALT = 10  # metres

m = mavutil.mavlink_connection("udp:127.0.0.1:14551")
m.wait_heartbeat()
print("Connected to system", m.target_system)

# Wait until the autopilot says it's ready to arm (EKF settled, GPS fix, checks passed).
print("Waiting for the autopilot to be ready to arm ...")
while True:
    status = m.recv_match(type="SYS_STATUS", blocking=True, timeout=5)
    if status and status.onboard_control_sensors_health & mavutil.mavlink.MAV_SYS_STATUS_PREARM_CHECK:
        break

m.set_mode("GUIDED")
m.arducopter_arm()
m.motors_armed_wait()
print("Armed")

m.mav.command_long_send(m.target_system, m.target_component,
                        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, TAKEOFF_ALT)

while True:
    pos = m.recv_match(type="GLOBAL_POSITION_INT", blocking=True)
    alt = pos.relative_alt / 1000
    print(f"altitude {alt:5.1f} m")
    if alt > TAKEOFF_ALT * 0.95:
        break

print("Reached altitude, hovering for 5 seconds")
time.sleep(5)
m.set_mode("LAND")
m.motors_disarmed_wait()
print("Landed and disarmed")
