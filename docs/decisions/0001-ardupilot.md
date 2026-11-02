# 0001. ArduPilot as the flight software

Date: 2026-09
Status: Accepted

## Context
The drone has to fly itself (hold position, return home, follow commands from a companion computer) and be controllable from my own code. I want to learn the tools autonomy teams actually use.

## Options
- **Betaflight / INAV:** great for manual FPV flying, but built around a pilot with sticks. Little support for a companion computer telling the drone where to go.
- **PX4:** a full autopilot with good ROS 2 support. A fine choice; smaller community for cheap hobby hardware.
- **ArduPilot:** a full autopilot, MAVLink everywhere, a large community, excellent simulator (SITL), and a native ROS 2 interface (DDS) since 4.5.

## Decision
ArduPilot Copter.

## Consequences
- Every script can be tested in SITL first, against the same firmware that flies.
- GUIDED mode lets the Pi command the drone over MAVLink.
- ROS 2 via DDS needs an H7 flight controller (see 0002) and a custom firmware build.
