# 0007. Patrol speaks MAVLink first, ROS 2 later

Date: 2026-10
Status: Accepted

## Context
The patrol needs to read the drone's position and attitude and send it where to go. Both MAVLink (pymavlink) and ROS 2 (ArduPilot's DDS interface) can do that.

## Options
- **ROS 2 from the start:** the "proper" robotics structure, but more moving parts (custom firmware, agent, containers) before anything flies.
- **MAVLink first:** one Python process, works with standard firmware, easy to test in SITL, well documented.

## Decision
Version 1 uses pymavlink. A ROS 2 version follows once version 1 works on the real drone.

## Consequences
- The serial link to the Pi runs MAVLink normally, and switches to DDS for ROS 2 sessions until a second UART is wired.
- The code is split (geometry, detector, mission) so the pieces can become ROS 2 nodes later.
